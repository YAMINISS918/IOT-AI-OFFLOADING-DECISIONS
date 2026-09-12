import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

# Load dataset
df = pd.read_csv("data/processed/processed_network_dataset.csv")

# Features
features = [
    "Bandwidth_Mbps",
    "Latency_ms",
    "CPU_Usage_percent",
    "Task_Size_MB"
]

data = df[features].values

# Normalize
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# Save scaler
os.makedirs("models", exist_ok=True)
joblib.dump(scaler, "models/main_feature_scaler.pkl")

# Create sequences
SEQUENCE_LENGTH = 10

X = []
y = []

for i in range(len(scaled_data) - SEQUENCE_LENGTH):
    X.append(scaled_data[i:i + SEQUENCE_LENGTH])
    y.append(scaled_data[i + SEQUENCE_LENGTH][1])  # Future latency

X = np.array(X)
y = np.array(y)

# Save
np.save("models/X_main.npy", X)
np.save("models/y_main.npy", y)

print("===== MAIN SEQUENCES CREATED =====")
print("X shape:", X.shape)
print("y shape:", y.shape)
print("Sequence length:", SEQUENCE_LENGTH)