import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib

# --------------------------------------------------
# Load sequence data
# --------------------------------------------------

X = np.load("X_sequences.npy")
y = np.load("y_latency.npy")

print("Original X shape:", X.shape)
print("Original y shape:", y.shape)

# --------------------------------------------------
# Chronological Train / Validation / Test split
# --------------------------------------------------

n = len(X)

train_end = int(n * 0.70)
val_end = int(n * 0.85)

X_train = X[:train_end]
X_val = X[train_end:val_end]
X_test = X[val_end:]

y_train = y[:train_end]
y_val = y[train_end:val_end]
y_test = y[val_end:]

print("\n===== DATA SPLIT =====")
print("Training:", len(X_train))
print("Validation:", len(X_val))
print("Testing:", len(X_test))

# --------------------------------------------------
# Normalize X
# --------------------------------------------------

# X shape:
# samples × sequence length × features

num_features = X_train.shape[2]

scaler_X = MinMaxScaler()

# Flatten training data temporarily
X_train_2d = X_train.reshape(-1, num_features)

# Fit scaler ONLY on training data
scaler_X.fit(X_train_2d)

# Transform all datasets
X_train_scaled = scaler_X.transform(
    X_train_2d
).reshape(X_train.shape)

X_val_scaled = scaler_X.transform(
    X_val.reshape(-1, num_features)
).reshape(X_val.shape)

X_test_scaled = scaler_X.transform(
    X_test.reshape(-1, num_features)
).reshape(X_test.shape)

# --------------------------------------------------
# Normalize target latency
# --------------------------------------------------

scaler_y = MinMaxScaler()

y_train_scaled = scaler_y.fit_transform(
    y_train.reshape(-1, 1)
).flatten()

y_val_scaled = scaler_y.transform(
    y_val.reshape(-1, 1)
).flatten()

y_test_scaled = scaler_y.transform(
    y_test.reshape(-1, 1)
).flatten()

# --------------------------------------------------
# Save processed data
# --------------------------------------------------

np.save("X_train.npy", X_train_scaled)
np.save("X_val.npy", X_val_scaled)
np.save("X_test.npy", X_test_scaled)

np.save("y_train.npy", y_train_scaled)
np.save("y_val.npy", y_val_scaled)
np.save("y_test.npy", y_test_scaled)

# Save scalers
joblib.dump(scaler_X, "feature_scaler.pkl")
joblib.dump(scaler_y, "latency_scaler.pkl")

# --------------------------------------------------
# Final information
# --------------------------------------------------

print("\n===== FINAL SHAPES =====")
print("X_train:", X_train_scaled.shape)
print("X_val:", X_val_scaled.shape)
print("X_test:", X_test_scaled.shape)

print("y_train:", y_train_scaled.shape)
print("y_val:", y_val_scaled.shape)
print("y_test:", y_test_scaled.shape)

print("\n===== COMPLETE =====")
print("Training, validation and testing data prepared.")
print("Scalers saved.")