import matplotlib.pyplot as plt

epochs = list(range(1, 11))
loss = [0.25,0.20,0.16,0.12,0.09,0.07,0.05,0.04,0.03,0.02]

plt.plot(epochs, loss)
plt.title("LSTM Training Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.grid(True)

plt.savefig("graphs/lstm_loss.png")
plt.show()