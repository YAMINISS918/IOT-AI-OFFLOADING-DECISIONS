import numpy as np
import matplotlib.pyplot as plt
import joblib

from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# --------------------------------------------------
# Load test data
# --------------------------------------------------

X_test = np.load("X_test.npy")
y_test_scaled = np.load("y_test.npy")

print("X_test shape:", X_test.shape)
print("y_test shape:", y_test_scaled.shape)


# --------------------------------------------------
# Load trained LSTM
# --------------------------------------------------

model = load_model("external_lstm_latency_model.keras")

print("\n===== MODEL LOADED =====")
print("external_lstm_latency_model.keras")


# --------------------------------------------------
# Load latency scaler
# --------------------------------------------------

latency_scaler = joblib.load("latency_scaler.pkl")


# --------------------------------------------------
# Predict
# --------------------------------------------------

y_pred_scaled = model.predict(
    X_test,
    verbose=1
)

y_pred_scaled = y_pred_scaled.flatten()


# --------------------------------------------------
# Convert normalized values back to milliseconds
# --------------------------------------------------

y_test = latency_scaler.inverse_transform(
    y_test_scaled.reshape(-1, 1)
).flatten()

y_pred = latency_scaler.inverse_transform(
    y_pred_scaled.reshape(-1, 1)
).flatten()


# --------------------------------------------------
# Calculate evaluation metrics
# --------------------------------------------------

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n===================================")
print("   LSTM LATENCY PREDICTION RESULTS")
print("===================================")

print(f"MAE  : {mae:.4f} ms")
print(f"RMSE : {rmse:.4f} ms")
print(f"R²   : {r2:.4f}")


# --------------------------------------------------
# Show sample predictions
# --------------------------------------------------

print("\n===== SAMPLE PREDICTIONS =====")

for i in range(min(20, len(y_test))):

    print(
        f"Sample {i+1:02d} | "
        f"Actual: {y_test[i]:.2f} ms | "
        f"Predicted: {y_pred[i]:.2f} ms"
    )


# --------------------------------------------------
# Actual vs Predicted graph
# --------------------------------------------------

samples_to_plot = min(200, len(y_test))

plt.figure(figsize=(12, 6))

plt.plot(
    y_test[:samples_to_plot],
    label="Actual Latency"
)

plt.plot(
    y_pred[:samples_to_plot],
    label="Predicted Latency"
)

plt.xlabel("Test Sample")
plt.ylabel("Latency (ms)")

plt.title(
    "Actual vs Predicted Future Latency"
)

plt.legend()
plt.grid(True)

plt.savefig(
    "actual_vs_predicted_latency.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# --------------------------------------------------
# Save predictions
# --------------------------------------------------

results = np.column_stack(
    (y_test, y_pred)
)

np.savetxt(
    "latency_predictions.csv",
    results,
    delimiter=",",
    header="Actual_Latency,Predicted_Latency",
    comments=""
)


print("\n===== COMPLETE =====")

print(
    "Graph saved: actual_vs_predicted_latency.png"
)

print(
    "Predictions saved: latency_predictions.csv"
)