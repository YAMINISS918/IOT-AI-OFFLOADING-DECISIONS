from tensorflow.keras.models import load_model
import numpy as np
import joblib


# ==========================================
# LOAD LSTM MODEL
# ==========================================

model = load_model(
    "models/main_lstm_model.keras"
)


# ==========================================
# LOAD FEATURE SCALER
# ==========================================

scaler = joblib.load(
    "models/main_feature_scaler.pkl"
)


# ==========================================
# PREDICT FUTURE LATENCY
# ==========================================

def predict_future_latency(network_history):

    # Need exactly 10 records
    if len(network_history) < 10:
        return None


    # Convert to numpy array
    network_data = np.array(
        network_history
    )


    # Normalize data
    scaled_data = scaler.transform(
        network_data
    )


    # Reshape for LSTM
    sequence = scaled_data.reshape(
        1,
        10,
        4
    )


    # Predict latency
    prediction_scaled = model.predict(
        sequence,
        verbose=0
    )[0][0]


    # ==========================================
    # INVERSE TRANSFORM
    # ==========================================

    dummy = np.zeros(
        (1, 4)
    )

    # Latency feature position = 1
    dummy[0][1] = prediction_scaled


    predicted_latency = scaler.inverse_transform(
        dummy
    )[0][1]


    # Prevent negative value
    predicted_latency = max(
        0,
        float(predicted_latency)
    )


    return round(
        predicted_latency,
        2
    )