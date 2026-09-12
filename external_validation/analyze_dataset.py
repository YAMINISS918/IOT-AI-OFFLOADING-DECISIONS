import pandas as pd

# Load dataset
df = pd.read_csv("task_offloading_dataset.csv")

print("\n===== BASIC INFORMATION =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n===== OFFLOADING DECISION COUNTS =====")
print(df["Offloading_Decision"].value_counts())

print("\n===== OFFLOADING DECISION PERCENTAGE =====")
print(df["Offloading_Decision"].value_counts(normalize=True) * 100)

print("\n===== LATENCY STATISTICS =====")
print(df["Latency"].describe())

print("\n===== THROUGHPUT STATISTICS =====")
print(df["Throughput"].describe())

print("\n===== UPLINK TRAFFIC STATISTICS =====")
print(df["Uplink_Traffic"].describe())

print("\n===== DOWNLINK TRAFFIC STATISTICS =====")
print(df["Downlink_Traffic"].describe())

print("\n===== DURATION STATISTICS =====")
print(df["Duration"].describe())

print("\n===== RAT COUNTS =====")
print(df["RAT"].value_counts())

print("\n===== CORRELATION WITH LATENCY =====")

numeric_columns = [
    "Downlink_Traffic",
    "Duration",
    "RAT",
    "Uplink_Traffic",
    "Latency",
    "Throughput"
]

print(df[numeric_columns].corr()["Latency"].sort_values(ascending=False))

print("\n===== LATENCY BY OFFLOADING DECISION =====")
print(df.groupby("Offloading_Decision")["Latency"].describe())

print("\n===== THROUGHPUT BY OFFLOADING DECISION =====")
print(df.groupby("Offloading_Decision")["Throughput"].describe())

print("\n===== DUPLICATES =====")
print("Duplicate rows:", df.duplicated().sum())