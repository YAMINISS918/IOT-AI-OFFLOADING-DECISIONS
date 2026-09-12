import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib


# ==========================================
# LOAD ORIGINAL DATASET
# ==========================================

df = pd.read_csv(
    "data/raw/network_dataset.csv"
)


# ==========================================
# SELECT FEATURES
# ==========================================

features = [
    "Bandwidth_Mbps",
    "Latency_ms",
    "CPU_Usage_percent",
    "Task_Size_MB"
]


data = df[features]


# ==========================================
# CREATE NEW SCALER
# ==========================================

scaler = MinMaxScaler()

scaler.fit(data)


# ==========================================
# SAVE CORRECT SCALER
# ==========================================

joblib.dump(
    scaler,
    "models/main_feature_scaler.pkl"
)


print("Scaler recreated successfully!")

print("\nFeature Minimum Values:")
print(scaler.data_min_)

print("\nFeature Maximum Values:")
print(scaler.data_max_)


# Test scaling

sample = [[
    85,
    20,
    30,
    5
]]

scaled = scaler.transform(sample)

print("\nOriginal:")
print(sample)

print("\nScaled:")
print(scaled)