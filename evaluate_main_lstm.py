
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("Loading model and test data...")

# Load the existing trained model and arrays
model = load_model("models/main_lstm_model.keras", compile=False)
X = np.load("models/X_main.npy")
y = np.load("models/y_main.npy").reshape(-1)

# Confirm array dimensions
print("Input shape:", X.shape)
print("Target shape:", y.shape)

if len(X) != len(y):
    raise ValueError("Input and target sample counts do not match.")

# Use the same chronological 80/20 split as training
split = int(len(X) * 0.8)
X_test = X[split:]
y_test = y[split:]

if len(X_test) == 0:
    raise ValueError("The test dataset is empty.")

# Predict using the same input representation used in training
predictions = model.predict(X_test, verbose=0).reshape(-1)

# Convert scaled latency values back to milliseconds
# only when the target appears to be normalized to [0, 1].
if (
    np.min(y) >= -0.001
    and np.max(y) <= 1.001
):
    scaler = joblib.load("models/main_feature_scaler.pkl")
    latency_min = scaler.data_min_[1]
    latency_max = scaler.data_max_[1]

    y_test = y_test * (latency_max - latency_min) + latency_min
    predictions = (
        predictions * (latency_max - latency_min) + latency_min
    )

    print("Target interpretation: scaled latency; converted to ms")
else:
    print("Target interpretation: original latency units")
    print("Verify these units against your training preprocessing.")

# Calculate evaluation metrics
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

print("\n===== MAIN LSTM TEST RESULTS =====")
print(f"Test samples: {len(y_test)}")
print(f"MAE:  {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R²:   {r2:.4f}")
print(f"Actual target range: {y_test.min():.4f} to {y_test.max():.4f}")
print(f"Prediction range:    {predictions.min():.4f} to {predictions.max():.4f}")

print("\nEvaluation finished.")
print("Note: Confirm target scaling and units before reporting results.")
