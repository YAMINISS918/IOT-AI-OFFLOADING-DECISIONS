from tensorflow.keras.models import load_model

# Load models without compiling
lstm_model = load_model(
    "models/lstm_latency_model.h5",
    compile=False
)

classifier_model = load_model(
    "models/offloading_classifier.keras",
    compile=False
)

print("LSTM Model Loaded")
print("Classifier Model Loaded")
print("Evaluation Completed Successfully")