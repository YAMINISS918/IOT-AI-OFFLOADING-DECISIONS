import numpy as np
import matplotlib.pyplot as plt

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# --------------------------------------------------
# Load prepared data
# --------------------------------------------------

X_train = np.load("X_train.npy")
X_val = np.load("X_val.npy")

y_train = np.load("y_train.npy")
y_val = np.load("y_val.npy")

print("X_train:", X_train.shape)
print("X_val:", X_val.shape)

# --------------------------------------------------
# Build LSTM model
# --------------------------------------------------

model = Sequential([
    LSTM(
        64,
        input_shape=(X_train.shape[1], X_train.shape[2]),
        return_sequences=False
    ),

    Dropout(0.2),

    Dense(32, activation="relu"),

    Dense(1)
])

# --------------------------------------------------
# Compile model
# --------------------------------------------------

model.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mae"]
)

# --------------------------------------------------
# Display model
# --------------------------------------------------

model.summary()

# --------------------------------------------------
# Early stopping
# --------------------------------------------------

early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

# --------------------------------------------------
# Train
# --------------------------------------------------

history = model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=30,
    batch_size=64,
    callbacks=[early_stopping],
    verbose=1
)

# --------------------------------------------------
# Save model
# --------------------------------------------------

model.save("external_lstm_latency_model.keras")

print("\n===== MODEL SAVED =====")
print("external_lstm_latency_model.keras")

# --------------------------------------------------
# Plot training and validation loss
# --------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    history.history["loss"],
    label="Training Loss"
)

plt.plot(
    history.history["val_loss"],
    label="Validation Loss"
)

plt.xlabel("Epoch")
plt.ylabel("MSE Loss")
plt.title("External LSTM Training and Validation Loss")

plt.legend()
plt.grid(True)

plt.savefig(
    "external_lstm_training_loss.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nGraph saved as:")
print("external_lstm_training_loss.png")