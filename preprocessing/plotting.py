import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

def plot_losses(training_losses, validation_losses, epochs):
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, training_losses, label='Training Loss', color='blue', marker='o')
    plt.plot(epochs, validation_losses, label='Validation Loss', color='red', marker='x')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

