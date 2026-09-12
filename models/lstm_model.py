import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split

# Load processed dataset
data = pd.read_csv("data/processed/processed_network_dataset.csv")

# Select features
features = data[[
    "Bandwidth_Mbps",
    "Latency_ms",
    "CPU_Usage_percent"
]].values

sequence_length = 5

X = []
y = []

# Create sequences
for i in range(len(features) - sequence_length):
    X.append(features[i:i+sequence_length])
    y.append(features[i+sequence_length][1])   # Predict latency

X = np.array(X)
y = np.array(y)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Build LSTM Model
model = Sequential()

model.add(LSTM(64, input_shape=(sequence_length, 3)))

model.add(Dense(1))

model.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mae"]
)

# Train
history = model.fit(
    X_train,
    y_train,
    epochs=10,
    batch_size=32,
    validation_data=(X_test, y_test)
)

# Save model
model.save("models/lstm_latency_model.h5")

print("LSTM Model Trained Successfully!")