import pandas as pd

df = pd.read_csv("task_offloading_cleaned.csv")

print("\n===== FIRST 30 RECORDS =====")

columns = [
    "Cell_Identity(CI)",
    "LAC",
    "RAT",
    "Latency",
    "Throughput",
    "Uplink_Traffic",
    "Downlink_Traffic",
    "Duration"
]

print(df[columns].head(30).to_string(index=True))


print("\n===== SAME CELL CONSECUTIVE OBSERVATIONS =====")

same_cell = (
    df["Cell_Identity(CI)"]
    .shift(1)
    .eq(df["Cell_Identity(CI)"])
)

print(
    "Consecutive rows belonging to same Cell ID:",
    same_cell.sum()
)

print(
    "Percentage:",
    same_cell.mean() * 100
)


print("\n===== SAME CELL + RAT CONSECUTIVE OBSERVATIONS =====")

same_group = (
    df["Cell_Identity(CI)"].shift(1).eq(df["Cell_Identity(CI)"])
    &
    df["RAT"].shift(1).eq(df["RAT"])
)

print(
    "Consecutive rows belonging to same Cell + RAT:",
    same_group.sum()
)

print(
    "Percentage:",
    same_group.mean() * 100
)


print("\n===== LATENCY CHANGE BETWEEN CONSECUTIVE ROWS =====")

latency_change = df["Latency"].diff().abs()

print(latency_change.describe())


print("\n===== THROUGHPUT CHANGE BETWEEN CONSECUTIVE ROWS =====")

throughput_change = df["Throughput"].diff().abs()

print(throughput_change.describe())