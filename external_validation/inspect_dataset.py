import pandas as pd

# Load Kaggle dataset
df = pd.read_csv("task_offloading_dataset.csv")

print("\n===== DATASET SHAPE =====")
print(df.shape)

print("\n===== COLUMN NAMES =====")
print(df.columns.tolist())

print("\n===== FIRST 10 RECORDS =====")
print(df.head(10))

print("\n===== DATA TYPES =====")
print(df.dtypes)

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== DUPLICATE ROWS =====")
print(df.duplicated().sum())

print("\n===== STATISTICAL SUMMARY =====")
print(df.describe(include="all"))