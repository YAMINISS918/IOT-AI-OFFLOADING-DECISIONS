import pandas as pd

# Load original Kaggle dataset
df = pd.read_csv("task_offloading_dataset.csv")

print("Original rows:", len(df))

# --------------------------------------------------
# 1. Remove exact duplicate rows
# --------------------------------------------------
df_clean = df.drop_duplicates().copy()

print("Rows after removing duplicates:", len(df_clean))
print("Duplicates removed:", len(df) - len(df_clean))

# --------------------------------------------------
# 2. Check invalid values
# --------------------------------------------------
print("\n===== INVALID VALUES =====")

print("Negative Latency:",
      (df_clean["Latency"] < 0).sum())

print("Negative Throughput:",
      (df_clean["Throughput"] < 0).sum())

print("Negative Uplink Traffic:",
      (df_clean["Uplink_Traffic"] < 0).sum())

print("Negative Downlink Traffic:",
      (df_clean["Downlink_Traffic"] < 0).sum())

print("Negative Duration:",
      (df_clean["Duration"] < 0).sum())

# --------------------------------------------------
# 3. Display latency percentiles
# --------------------------------------------------
print("\n===== LATENCY PERCENTILES =====")

print(df_clean["Latency"].quantile(
    [0.50, 0.75, 0.90, 0.95, 0.99, 0.995, 0.999]
))

# --------------------------------------------------
# 4. Display throughput percentiles
# --------------------------------------------------
print("\n===== THROUGHPUT PERCENTILES =====")

print(df_clean["Throughput"].quantile(
    [0.50, 0.75, 0.90, 0.95, 0.99, 0.999]
))

# --------------------------------------------------
# 5. Save cleaned dataset
# --------------------------------------------------
output_file = "task_offloading_cleaned.csv"

df_clean.to_csv(output_file, index=False)

print("\n===== COMPLETE =====")
print("Cleaned dataset saved as:", output_file)