import pandas as pd

# Load cleaned dataset
df = pd.read_csv("task_offloading_cleaned.csv")

print("\n===== DATASET SIZE =====")
print("Rows:", len(df))

# --------------------------------------------------
# 1. Unique network contexts
# --------------------------------------------------

print("\n===== UNIQUE VALUES =====")

print("Unique Cell IDs:",
      df["Cell_Identity(CI)"].nunique())

print("Unique LAC:",
      df["LAC"].nunique())

print("Unique RAT:",
      df["RAT"].nunique())

# --------------------------------------------------
# 2. Number of records per Cell ID
# --------------------------------------------------

print("\n===== RECORDS PER CELL ID =====")

cell_counts = df["Cell_Identity(CI)"].value_counts()

print(cell_counts.describe())

print("\nTop 10 Cell IDs:")
print(cell_counts.head(10))

# --------------------------------------------------
# 3. Number of records per Cell + RAT
# --------------------------------------------------

print("\n===== RECORDS PER CELL + RAT =====")

group_counts = (
    df.groupby(["Cell_Identity(CI)", "RAT"])
      .size()
      .sort_values(ascending=False)
)

print(group_counts.head(20))

# --------------------------------------------------
# 4. Check whether enough sequences exist
# --------------------------------------------------

sequence_length = 10

print("\n===== SEQUENCE AVAILABILITY =====")

groups_with_10 = (group_counts >= sequence_length).sum()

print(
    "Cell + RAT groups with at least",
    sequence_length,
    "records:",
    groups_with_10
)

# --------------------------------------------------
# 5. Latency statistics by RAT
# --------------------------------------------------

print("\n===== LATENCY BY RAT =====")

print(
    df.groupby("RAT")["Latency"].describe()
)

# --------------------------------------------------
# 6. Throughput statistics by RAT
# --------------------------------------------------

print("\n===== THROUGHPUT BY RAT =====")

print(
    df.groupby("RAT")["Throughput"].describe()
)
