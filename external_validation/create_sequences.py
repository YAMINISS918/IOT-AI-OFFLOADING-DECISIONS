import pandas as pd
import numpy as np

# --------------------------------------------------
# Load cleaned dataset
# --------------------------------------------------

df = pd.read_csv("task_offloading_cleaned.csv")

print("Total rows:", len(df))

# --------------------------------------------------
# Sort by Cell ID and RAT
# --------------------------------------------------

df = df.sort_values(
    ["Cell_Identity(CI)", "RAT"]
).reset_index(drop=True)

# --------------------------------------------------
# Features used for LSTM
# --------------------------------------------------

features = [
    "Downlink_Traffic",
    "Uplink_Traffic",
    "Throughput",
    "Latency",
    "RAT"
]

target = "Latency"

sequence_length = 10

# --------------------------------------------------
# Create sequences
# --------------------------------------------------

X = []
y = []

grouped = df.groupby(
    ["Cell_Identity(CI)", "RAT"],
    sort=False
)

for (cell_id, rat), group in grouped:

    group = group.reset_index(drop=True)

    # Skip groups with insufficient observations
    if len(group) <= sequence_length:
        continue

    values = group[features].values
    latency_values = group[target].values

    for i in range(len(group) - sequence_length):

        sequence = values[i:i + sequence_length]

        future_latency = latency_values[i + sequence_length]

        X.append(sequence)
        y.append(future_latency)

X = np.array(X)
y = np.array(y)

# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n===== SEQUENCE DATASET =====")

print("X shape:", X.shape)
print("y shape:", y.shape)

print("\nNumber of sequences:", len(X))

print("\nSequence length:", sequence_length)

print("\nNumber of features:", len(features))

print("\nFeatures:")
for feature in features:
    print("-", feature)

print("\nTarget: Future Latency")

# --------------------------------------------------
# Save
# --------------------------------------------------

np.save("X_sequences.npy", X)
np.save("y_latency.npy", y)

print("\n===== COMPLETE =====")
print("Saved:")
print("X_sequences.npy")
print("y_latency.npy")