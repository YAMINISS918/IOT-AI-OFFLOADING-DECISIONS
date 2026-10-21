
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import MinMaxScaler

# Load raw dataset
df = pd.read_csv("data/raw/network_dataset.csv")

features = [
    "Bandwidth_Mbps",
    "Latency_ms",
    "CPU_Usage_percent",
    "Task_Size_MB"
]

data = df[features].values
scenarios = df["Scenario"].values

SEQUENCE_LENGTH = 10
split_row = int(len(data) * 0.8)

# Fit scaler only on the training period
scaler = MinMaxScaler()
scaler.fit(data[:split_row])
scaled_data = scaler.transform(data)

X, y, scenario_labels = [], [], []

for i in range(len(scaled_data) - SEQUENCE_LENGTH):
    X.append(scaled_data[i:i + SEQUENCE_LENGTH])
    y.append(scaled_data[i + SEQUENCE_LENGTH, 1])
    scenario_labels.append(scenarios[i + SEQUENCE_LENGTH])

X = np.array(X)
y = np.array(y)
scenario_labels = np.array(scenario_labels)

os.makedirs("models", exist_ok=True)

joblib.dump(scaler, "models/main_feature_scaler.pkl")
np.save("models/X_main.npy", X)
np.save("models/y_main.npy", y)
np.save("models/scenario_labels.npy", scenario_labels)

print("Sequences created from raw data.")
print("X shape:", X.shape)
print("y shape:", y.shape)
print("Scenario labels shape:", scenario_labels.shape)
print("Scenario counts:")
print(pd.Series(scenario_labels).value_counts())
print("Scaler fitted on training-period data.")
