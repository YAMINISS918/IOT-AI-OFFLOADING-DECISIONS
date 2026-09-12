from lstm_predictor import model, scaler
import numpy as np


# Sample realistic network history
history = np.array([
    [85, 20, 30, 5],
    [82, 22, 32, 4],
    [80, 25, 35, 6],
    [75, 30, 40, 5],
    [70, 35, 45, 7],
    [65, 40, 50, 6],
    [60, 50, 55, 8],
    [50, 65, 60, 7],
    [40, 80, 70, 9],
    [30, 100, 80, 8]
])


print("\n===== ORIGINAL INPUT =====")
print(history)


# Scale input
scaled = scaler.transform(history)

print("\n===== SCALED INPUT =====")
print(scaled)


# Reshape
sequence = scaled.reshape(1, 10, 4)


# Model prediction
prediction = model.predict(
    sequence,
    verbose=0
)[0][0]


print("\n===== RAW MODEL OUTPUT =====")
print(prediction)


# Inverse transform
dummy = np.zeros((1, 4))
dummy[0][1] = prediction

inverse = scaler.inverse_transform(dummy)[0][1]

print("\n===== INVERSE PREDICTED LATENCY =====")
print(inverse)