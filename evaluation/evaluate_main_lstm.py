
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

X = np.load("models/X_main.npy")
y = np.load("models/y_main.npy").reshape(-1)
scaler = joblib.load("models/main_feature_scaler.pkl")
model = load_model("models/main_lstm_model.keras", compile=False)

# Same chronological split as training
train_end = int(len(X) * 0.70)
val_end = int(len(X) * 0.80)

X_test = X[val_end:]
y_test = y[val_end:]

pred_scaled = model.predict(X_test, verbose=0).reshape(-1)

# Convert normalized latency to milliseconds
latency_min = scaler.data_min_[1]
latency_max = scaler.data_max_[1]
y_true = y_test * (latency_max - latency_min) + latency_min
y_pred = pred_scaled * (latency_max - latency_min) + latency_min

# Baseline uses the training target mean only
baseline_scaled = np.full_like(y_test, np.mean(y[:train_end]))
baseline_pred = baseline_scaled * (latency_max - latency_min) + latency_min

print("\n===== FINAL TEST: LSTM VS BASELINE =====")
print("Test samples:", len(y_test))

for name, pred in [("LSTM", y_pred), ("Baseline", baseline_pred)]:
    print(f"\n{name}")
    print(f"MAE:  {mean_absolute_error(y_true, pred):.3f} ms")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_true, pred)):.3f} ms")
    print(f"R2:   {r2_score(y_true, pred):.4f}")

print(f"\nActual latency range: {y_true.min():.2f} to {y_true.max():.2f} ms")
print(f"Predicted latency range: {y_pred.min():.2f} to {y_pred.max():.2f} ms")
