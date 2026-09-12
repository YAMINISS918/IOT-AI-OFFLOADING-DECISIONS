from lstm_predictor import model, scaler
import numpy as np

print("Scaler feature count:")
print(scaler.n_features_in_)

print("\nScaler minimum:")
print(scaler.data_min_)

print("\nScaler maximum:")
print(scaler.data_max_)

print("\nModel input shape:")
print(model.input_shape)

print("\nModel output shape:")
print(model.output_shape)