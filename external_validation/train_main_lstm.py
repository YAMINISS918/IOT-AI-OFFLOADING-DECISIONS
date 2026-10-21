
import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

X = np.load("models/X_main.npy")
y = np.load("models/y_main.npy")
scenarios = np.load("models/scenario_labels.npy")

# Stratified split: all scenarios represented in each subset
indices = np.arange(len(X))
train_idx, temp_idx = train_test_split(
    indices,
    test_size=0.30,
    random_state=42,
    stratify=scenarios
)

val_idx, test_idx = train_test_split(
    temp_idx,
    test_size=2/3,
    random_state=42,
    stratify=scenarios[temp_idx]
)

X_train, y_train = X[train_idx], y[train_idx]
X_val, y_val = X[val_idx], y[val_idx]
X_test, y_test = X[test_idx], y[test_idx]

print("Training samples:", len(X_train))
print("Validation samples:", len(X_val))
print("Test samples:", len(X_test))

for name, idx in [
    ("Train", train_idx),
    ("Validation", val_idx),
    ("Test", test_idx)
]:
    print(f"\n{name} scenario counts:")
    print({s: int(np.sum(scenarios[idx] == s))
           for s in np.unique(scenarios)})

model = Sequential([
    Input(shape=(X.shape[1], X.shape[2])),
    LSTM(64),
    Dropout(0.2),
    Dense(32, activation="relu"),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse", metrics=["mae"])

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=30,
    batch_size=32,
    callbacks=[early_stop],
    shuffle=True,
    verbose=1
)

os.makedirs("models", exist_ok=True)
model.save("models/main_lstm_model.keras")
np.save("models/X_test_stratified.npy", X_test)
np.save("models/y_test_stratified.npy", y_test)
np.save("models/test_scenarios_stratified.npy", scenarios[test_idx])

print("\nModel saved successfully.")
print("Stratified test data saved for evaluation.")
