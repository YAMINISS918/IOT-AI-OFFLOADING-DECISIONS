import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Load processed dataset
data = pd.read_csv("data/processed/processed_network_dataset.csv")

# Input features
X = data[[
    "Bandwidth_Mbps",
    "Latency_ms",
    "CPU_Usage_percent",
    "Task_Size_MB"
]]

# Target
y = data["Offloading_Decision"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Build Neural Network
model = Sequential()

model.add(Dense(16, activation="relu", input_shape=(4,)))
model.add(Dense(8, activation="relu"))
model.add(Dense(1, activation="sigmoid"))

# Compile
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# Train
model.fit(
    X_train,
    y_train,
    epochs=10,
    batch_size=32,
    validation_data=(X_test, y_test)
)

# Save
model.save("models/offloading_classifier.keras")

print("Classifier trained successfully!")