from fastapi import FastAPI, UploadFile, File
from tensorflow.keras.models import load_model
from network_analyzer import analyze_network
from decision_engine import make_offloading_decision
import numpy as np
import joblib


app = FastAPI(title="IoT Intelligent Offloading API")


# ---------------------------------------------------------
# LOAD MODEL AND SCALER
# ---------------------------------------------------------

model = load_model("models/main_lstm_model.keras")
scaler = joblib.load("models/main_feature_scaler.pkl")


# ---------------------------------------------------------
# REAL-TIME MONITORING VARIABLES
# ---------------------------------------------------------

network_history = []

current_task_size_mb = 0.01
current_file_name = ""


# ---------------------------------------------------------
# MANUAL INPUT HISTORY
# ---------------------------------------------------------

manual_history = []


# =========================================================
# REAL-TIME START
# =========================================================

@app.post("/realtime/start")
async def start_realtime(file: UploadFile = File(...)):

    global network_history
    global current_task_size_mb
    global current_file_name

    file_content = await file.read()

    file_size_bytes = len(file_content)

    current_task_size_mb = file_size_bytes / (1024 * 1024)

    current_task_size_mb = max(current_task_size_mb, 0.01)

    current_file_name = file.filename

    # Start a fresh monitoring session
    network_history = []

    return {
        "status": "monitoring_started",
        "file_name": current_file_name,
        "task_size_mb": round(current_task_size_mb, 2),
        "records_collected": 0,
        "records_needed": 10,
        "message": "IoT task registered successfully. Real-time monitoring can now begin."
    }


# =========================================================
# REAL-TIME MEASUREMENT
# =========================================================

@app.post("/realtime/measure")
async def realtime_measure(data: dict):

    global network_history
    global current_task_size_mb

    bandwidth = float(data.get("bandwidth", 0))

    latency = data.get("latency")

    cpu = float(data.get("cpu_usage", 0))

    task_size_mb = float(
        data.get("task_size", current_task_size_mb)
    )

    if latency is None:
        return {
            "status": "error",
            "message": "Could not measure network latency."
        }

    latency = float(latency)

    # Add current measurement
    network_history.append([
        bandwidth,
        latency,
        cpu,
        task_size_mb
    ])

    # Keep only latest 10 records
    if len(network_history) > 10:
        network_history.pop(0)

    # Analyze network condition
    network_analysis = analyze_network(network_history)

    # -----------------------------------------------------
    # WAIT UNTIL 10 RECORDS ARE AVAILABLE
    # -----------------------------------------------------

    if len(network_history) < 10:

        return {
            "status": "collecting_data",
            "records_collected": len(network_history),
            "records_needed": 10,
            "file_name": current_file_name,
            "task_size_mb": round(task_size_mb, 2),

            "current_data": {
                "bandwidth": bandwidth,
                "latency": latency,
                "cpu_usage": cpu
            },

            "network_condition": network_analysis
        }

    # -----------------------------------------------------
    # LSTM PREDICTION
    # -----------------------------------------------------

    try:

        history_array = np.array(
            network_history,
            dtype=float
        )

        # Scale input
        sequence_scaled = scaler.transform(
            history_array
        )

        # LSTM input shape:
        # (batch, time steps, features)

        sequence_scaled = sequence_scaled.reshape(
            1,
            10,
            4
        )

        # Predict future latency
        prediction_scaled = model.predict(
            sequence_scaled,
            verbose=0
        )[0][0]

        # Convert predicted latency back
        # to original milliseconds

        dummy = np.zeros((1, 4))

        dummy[0][1] = prediction_scaled

        predicted_latency = scaler.inverse_transform(
            dummy
        )[0][1]

        predicted_latency = max(
            0,
            float(predicted_latency)
        )

    except Exception as e:

        return {
            "status": "prediction_error",
            "message": str(e)
        }

    # -----------------------------------------------------
    # OFFLOADING DECISION
    # -----------------------------------------------------

    decision_result = make_offloading_decision(
        predicted_latency,
        cpu,
        task_size_mb
    )

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return {

        "status": "prediction_complete",

        "file_name": current_file_name,

        "task_size_mb": round(
            task_size_mb,
            2
        ),

        "current_bandwidth": round(
            bandwidth,
            2
        ),

        "current_latency": round(
            latency,
            2
        ),

        "cpu_usage": round(
            cpu,
            2
        ),

        "predicted_latency": round(
            predicted_latency,
            2
        ),

        "network_condition": network_analysis,

        "recommended_execution":
            decision_result["decision"],

        "decision_score":
            decision_result["score"],

        "reasons":
            decision_result["reasons"],

        "records_collected":
            len(network_history),

        "records_needed":
            10
    }


# =========================================================
# MANUAL PREDICTION
# =========================================================

@app.post("/predict")
async def manual_predict(data: dict):

    global manual_history

    try:

        bandwidth = float(
            data.get("bandwidth", 0)
        )

        latency = float(
            data.get("latency", 0)
        )

        cpu = float(
            data.get("cpu_usage", 0)
        )

        task_size = float(
            data.get("task_size", 0.01)
        )

        # -------------------------------------------------
        # CREATE CURRENT MANUAL RECORD
        # -------------------------------------------------

        current_record = [
            bandwidth,
            latency,
            cpu,
            task_size
        ]

        manual_history.append(current_record)

        # Keep latest 10
        if len(manual_history) > 10:
            manual_history.pop(0)

        # -------------------------------------------------
        # LSTM NEEDS 10 TIME STEPS
        # -------------------------------------------------

        history_for_prediction = list(
            manual_history
        )

        # If fewer than 10 records exist,
        # repeat the first/current observation
        # so the model receives the required shape.

        while len(history_for_prediction) < 10:

            history_for_prediction.insert(
                0,
                history_for_prediction[0]
            )

        # Keep exactly 10
        history_for_prediction = \
            history_for_prediction[-10:]

        # -------------------------------------------------
        # NETWORK ANALYSIS
        # -------------------------------------------------

        network_analysis = analyze_network(
            history_for_prediction
        )

        # -------------------------------------------------
        # SCALE DATA
        # -------------------------------------------------

        history_array = np.array(
            history_for_prediction,
            dtype=float
        )

        sequence_scaled = scaler.transform(
            history_array
        )

        sequence_scaled = sequence_scaled.reshape(
            1,
            10,
            4
        )

        # -------------------------------------------------
        # LSTM PREDICTION
        # -------------------------------------------------

        prediction_scaled = model.predict(
            sequence_scaled,
            verbose=0
        )[0][0]

        # Convert prediction back to milliseconds

        dummy = np.zeros((1, 4))

        dummy[0][1] = prediction_scaled

        predicted_latency = scaler.inverse_transform(
            dummy
        )[0][1]

        predicted_latency = max(
            0,
            float(predicted_latency)
        )

        # -------------------------------------------------
        # DECISION ENGINE
        # -------------------------------------------------

        decision_result = make_offloading_decision(
            predicted_latency,
            cpu,
            task_size
        )

        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        return {

            "status": "prediction_complete",

            "input_data": {

                "bandwidth": round(
                    bandwidth,
                    2
                ),

                "latency": round(
                    latency,
                    2
                ),

                "cpu_usage": round(
                    cpu,
                    2
                ),

                "task_size": round(
                    task_size,
                    2
                )
            },

            "predicted_latency": round(
                predicted_latency,
                2
            ),

            "network_condition":
                network_analysis,

            "recommended_execution":
                decision_result["decision"],

            "decision_score":
                decision_result["score"],

            "reasons":
                decision_result["reasons"],

            "records_used":
                len(history_for_prediction)
        }

    except Exception as e:

        return {
            "status": "prediction_error",
            "message": str(e)
        }


# =========================================================
# RESET REAL-TIME MONITORING
# =========================================================

@app.post("/realtime/reset")
async def reset_realtime():

    global network_history
    global current_task_size_mb
    global current_file_name
    global manual_history

    network_history = []

    manual_history = []

    current_task_size_mb = 0.01

    current_file_name = ""

    return {
        "status": "reset",
        "message": "Real-time monitoring reset successfully."
    }


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "status": "running",
        "message": "IoT Intelligent Offloading API is running."
    }