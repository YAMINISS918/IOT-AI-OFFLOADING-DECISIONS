import pandas as pd

df = pd.read_csv("network_dataset.csv")

print("\n===== DATASET SIZE =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n===== SCENARIO COUNTS =====")
print(df["Scenario"].value_counts())

print("\n===== SCENARIO PERCENTAGE =====")
print(df["Scenario"].value_counts(normalize=True) * 100)

print("\n===== BANDWIDTH BY SCENARIO =====")
print(df.groupby("Scenario")["Bandwidth_Mbps"].describe())

print("\n===== LATENCY BY SCENARIO =====")
print(df.groupby("Scenario")["Latency_ms"].describe())

print("\n===== CPU USAGE BY SCENARIO =====")
print(df.groupby("Scenario")["CPU_Usage_percent"].describe())

print("\n===== TASK SIZE BY SCENARIO =====")
print(df.groupby("Scenario")["Task_Size_MB"].describe())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== DUPLICATES =====")
print(df.duplicated().sum())

print("\n===== TIME CHECK =====")
print("Minimum Time:", df["Time"].min())
print("Maximum Time:", df["Time"].max())
print("Time values unique:", df["Time"].is_unique)
print("Time sorted:", df["Time"].is_monotonic_increasing)
