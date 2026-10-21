
from collections import deque
from threading import Lock
from contextlib import asynccontextmanager
from typing import Optional
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from tensorflow.keras.models import load_model

from decision_engine import make_adaptive_offloading_decision


# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "main_lstm_model.keras"
SCALER_PATH = BASE_DIR / "models" / "main_feature_scaler.pkl"

FEATURES = ["bandwidth", "latency", "cpu_usage", "task_size"]
WINDOW = 10

state = {}
histories = {}
last_pred = {}
lock = Lock()


# ==========================================
# LOAD MODEL
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found: {MODEL_PATH}")

    if not SCALER_PATH.exists():
        raise RuntimeError(f"Scaler not found: {SCALER_PATH}")

    state["model"] = load_model(str(MODEL_PATH))
    state["scaler"] = joblib.load(SCALER_PATH)

    # Confirm the expected input shape
    expected_shape = state["model"].input_shape
    if len(expected_shape) != 3 or expected_shape[1:] != (WINDOW, len(FEATURES)):
        raise RuntimeError(
            f"Model input shape is {expected_shape}; "
            f"expected (None, {WINDOW}, {len(FEATURES)})"
        )

    if getattr(state["scaler"], "n_features_in_", len(FEATURES)) != len(FEATURES):
        raise RuntimeError(
            "Scaler must be fitted on the four input features."
        )

    yield
    state.clear()


app = FastAPI(
    title="IoT Intelligent Edge-Cloud Offloading API",
    version="1.0.0",
    lifespan=lifespan
)


# ==========================================
# REQUEST SCHEMA
# ==========================================

class PredictRequest(BaseModel):
    device_id: str = Field(default="default", min_length=1, max_length=100)
    bandwidth: float = Field(ge=0)
    latency: float = Field(ge=0)
    cpu_usage: float = Field(ge=0, le=100)
    task_size: float = Field(ge=0)
    task_priority: str = "normal"
    data_is_fresh: bool = True
    edge_available: bool = True


# ==========================================
# NETWORK CONDITION
# ==========================================

def get_network_condition(history):
    latencies = [row[1] for row in history]
    bandwidths = [row[0] for row in history]

    avg_latency = float(np.mean(latencies))
    variation = float(np.std(latencies))
    avg_bandwidth = float(np.mean(bandwidths))

    if variation > 20 or avg_latency > 150:
        condition = "UNSTABLE"
    else:
        condition = "STABLE"

    return {
        "condition": condition,
        "average_latency": round(avg_latency, 2),
        "latency_variation": round(variation, 2),
        "average_bandwidth": round(avg_bandwidth, 2)
    }


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "message": "IoT Intelligent Edge-Cloud Offloading API Running",
        "docs": "/docs",
        "features": [
            "LSTM latency prediction",
            "Adaptive offloading decision",
            "Network condition monitoring",
            "Device-wise history",
            "Prediction error monitoring"
        ]
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": "model" in state,
        "scaler_loaded": "scaler" in state
    }


# ==========================================
# RESET HISTORY
# ==========================================

@app.post("/reset")
def reset(device_id: Optional[str] = None):
    with lock:
        if device_id:
            histories.pop(device_id, None)
            last_pred.pop(device_id, None)
            message = f"History reset for device {device_id}"
        else:
            histories.clear()
            last_pred.clear()
            message = "All network histories reset successfully"

    return {"message": message}


# ==========================================
# PREDICTION
# ==========================================

@app.post("/predict")
def predict(req: PredictRequest):

    # Collect one device's history safely
    with lock:
        hist = histories.setdefault(
            req.device_id,
            deque(maxlen=WINDOW)
        )

        previous_prediction = last_pred.get(req.device_id)

        # Compare the previous prediction with current observed latency.
        # This is a rough error estimate, not a formally aligned evaluation.
        error_ms = (
            abs(previous_prediction - req.latency)
            if previous_prediction is not None
            else None
        )

        hist.append([
            req.bandwidth,
            req.latency,
            req.cpu_usage,
            req.task_size
        ])

        if len(hist) < WINDOW:
            return {
                "status": "collecting_data",
                "device_id": req.device_id,
                "records_collected": len(hist),
                "records_needed": WINDOW
            }

        history_snapshot = list(hist)

    # Check that the model and scaler are ready
    if "model" not in state or "scaler" not in state:
        raise HTTPException(
            status_code=503,
            detail="Model or scaler is not loaded"
        )

    # ======================================
    # PREPARE LSTM INPUT
    # ======================================

    try:
        window_df = pd.DataFrame(
            history_snapshot,
            columns=FEATURES
        )

        scaled = state["scaler"].transform(window_df)

        x = scaled.reshape(
            1,
            WINDOW,
            len(FEATURES)
        ).astype("float32")

        # ==================================
        # PREDICT LATENCY
        # ==================================

        prediction = state["model"].predict(x, verbose=0)
        pred_scaled = float(np.asarray(prediction).reshape(-1)[0])

        # Inverse-transform latency using the same four-feature scaler.
        dummy = np.zeros((1, len(FEATURES)))
        dummy[0, 1] = pred_scaled

        predicted_latency = float(
            state["scaler"].inverse_transform(dummy)[0, 1]
        )

        predicted_latency = max(0.0, predicted_latency)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}"
        ) from exc

    # Save latest prediction for this device
    with lock:
        last_pred[req.device_id] = predicted_latency

    # ======================================
    # NETWORK MONITORING
    # ======================================

    network_condition = get_network_condition(history_snapshot)

    # ======================================
    # ADAPTIVE OFFLOADING DECISION
    # ======================================

    result = make_adaptive_offloading_decision(
        network_condition=network_condition["condition"],
        predicted_latency=predicted_latency,
        cpu_usage=req.cpu_usage,
        task_size=req.task_size,
        task_priority=req.task_priority,
        data_is_fresh=req.data_is_fresh,
        prediction_error_ms=error_ms,
        edge_available=req.edge_available
    )

    # ======================================
    # RESPONSE
    # ======================================

    return {
        "status": "prediction_complete",
        "device_id": req.device_id,
        "input_data": {
            "bandwidth": req.bandwidth,
            "latency": req.latency,
            "cpu_usage": req.cpu_usage,
            "task_size": req.task_size
        },
        "predicted_latency": round(predicted_latency, 2),
        "prediction_error_ms": (
            None if error_ms is None else round(error_ms, 2)
        ),
        "network_condition": network_condition,
        "recommended_execution": result["decision"],
        "decision_status": result["status"],
        "reasons": result["reasons"],
        "records_used": WINDOW
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
