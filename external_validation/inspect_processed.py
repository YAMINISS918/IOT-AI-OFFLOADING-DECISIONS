import pandas as pd

df = pd.read_csv("data/processed/processed_network_dataset.csv")

print("\n===== PROCESSED DATASET =====")

print("\nColumns:")
print(df.columns.tolist())

print("\nShape:")
print(df.shape)

print("\nFirst 10 rows:")
print(df.head(10))

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nStatistics:")
print(df.describe())