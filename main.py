from fastapi import FastAPI
from tensorflow.keras.models import load_model
import numpy as np
import joblib

from decision_engine import make_offloading_decision


app = FastAPI(
    title="IoT Intelligent Offloading API"
)


# ==========================================
# LOAD TRAINED AI MODEL
# ==========================================

model = load_model("models/main_lstm_model.keras")

# Load scaler
scaler = joblib.load("models/main_feature_scaler.pkl")


# ==========================================
# NETWORK HISTORY
# ==========================================

network_history = []


# ==========================================
# HOME API
# ==========================================

@app.get("/")
def home():

    return {
        "message": "IoT Intelligent Edge-Cloud Offloading API Running"
    }


# ==========================================
# RESET HISTORY
# ==========================================

@app.post("/reset")
def reset_history():

    global network_history

    network_history = []

    return {
        "message": "Network history reset successfully"
    }


# ==========================================
# PREDICTION API
# ==========================================

@app.post("/predict")
def predict(data: dict):

    global network_history

    bandwidth = float(data["bandwidth"])
    latency = float(data["latency"])
    cpu = float(data["cpu_usage"])
    task_size = float(data["task_size"])


    # --------------------------------------
    # STORE NETWORK DATA
    # --------------------------------------

    network_history.append([
        bandwidth,
        latency,
        cpu,
        task_size
    ])


    # Keep only latest 10 records

    if len(network_history) > 10:
        network_history.pop(0)


    # --------------------------------------
    # WAIT FOR 10 RECORDS
    # --------------------------------------

    if len(network_history) < 10:

        return {
            "status": "collecting_data",
            "records_collected": len(network_history),
            "records_needed": 10
        }


    # --------------------------------------
    # NORMALIZE DATA
    # --------------------------------------

    sequence = scaler.transform(network_history)


    # --------------------------------------
    # RESHAPE FOR LSTM
    # --------------------------------------

    sequence = np.array(sequence).reshape(
        1,
        10,
        4
    )


    # --------------------------------------
    # PREDICT FUTURE LATENCY
    # --------------------------------------

    prediction_scaled = model.predict(
        sequence,
        verbose=0
    )[0][0]


    # --------------------------------------
    # CONVERT BACK TO ORIGINAL SCALE
    # --------------------------------------

    dummy = np.zeros((1, 4))

    # Latency is index 1
    dummy[0][1] = prediction_scaled

    predicted_latency = scaler.inverse_transform(
        dummy
    )[0][1]


    # Prevent negative latency

    predicted_latency = max(
        0,
        float(predicted_latency)
    )


    # --------------------------------------
    # EDGE / CLOUD DECISION
    # --------------------------------------

    decision_result = make_offloading_decision(
        predicted_latency,
        cpu,
        task_size
    )


    # --------------------------------------
    # RETURN RESULT
    # --------------------------------------

    return {

        "status": "prediction_complete",

        "current_bandwidth": bandwidth,

        "current_latency": latency,

        "cpu_usage": cpu,

        "task_size": task_size,

        "predicted_latency": round(
            predicted_latency,
            2
        ),

        "recommended_execution":
            decision_result["decision"],

        "decision_score":
            decision_result["score"],

        "reasons":
            decision_result["reasons"]

    }