import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# Load dataset
data = pd.read_csv("data/raw/network_dataset.csv")

# Encode Scenario
encoder = LabelEncoder()
data["Scenario"] = encoder.fit_transform(data["Scenario"])

# Create Offloading Decision
data["Offloading_Decision"] = (
    (data["Latency_ms"] > 100) |
    (data["CPU_Usage_percent"] > 80) |
    (data["Bandwidth_Mbps"] < 30)
).astype(int)

# Normalize numerical columns
scaler = MinMaxScaler()

columns = [
    "Bandwidth_Mbps",
    "Latency_ms",
    "CPU_Usage_percent",
    "Task_Size_MB"
]

data[columns] = scaler.fit_transform(data[columns])

# Save processed dataset
data.to_csv(
    "data/processed/processed_network_dataset.csv",
    index=False
)

print(data.head())