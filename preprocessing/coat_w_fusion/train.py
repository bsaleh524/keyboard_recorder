import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.transforms import Compose, ToTensor
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import librosa
import os
from CoAtNet import CoAtNet
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(device)

keyboard_dict = { # make lowercase
    0: '`', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: '-', 12: '=',
    13: 'q', 14: 'w', 15: 'e', 16: 'r', 17: 't', 18: 'y', 19: 'u', 20: 'i', 21: 'o', 22: 'p', 23: '[', 24: ']', 25:'bcksl',
    26: 'a', 27: 's', 28: 'd', 29: 'f', 30: 'g', 31: 'h', 32: 'j', 33: 'k', 34: 'l', 35: ';', 36: 'apost',
    37: 'z', 38: 'x', 39: 'c', 40: 'v', 41: 'b', 42: 'n', 43: 'm', 44: ',', 45: '.', 46: 'fwdsl', 47: 'space',
}
keyboard_reverse_map = {v: k for k, v in keyboard_dict.items()}
# Assume we have the following paths. Depend on your system, it could vary
AUDIO_DIR = 'preprocessed_data/'
MODEL_PATH = 'models/model.pt'


# The following class help transform our input into mel-spectrogram
class ToMelSpectrogram:
    def __call__(self, samples):
        return librosa.feature.melspectrogram(samples, n_mels=64, win_length=1024, hop_length=500)


# This class is to load audio data and apply the transformation
class AudioDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.file_list = os.listdir(self.data_dir)

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        waveform, _ = librosa.load(os.path.join(self.data_dir, self.file_list[idx]),
                                   sr=None,
                                   duration=1.0,
                                   mono=True)

        label_char = self.file_list[idx].split("_")[2]  # Assuming the file name is 'label_otherInfo.wav'

        # Encode the label using char_to_idx dictionary
        label = keyboard_reverse_map[label_char]

        if self.transform:
            waveform = self.transform(waveform)

        return waveform, label


def train():
    # We will use the transformation to convert the audio into Mel spectrogram
    transform = Compose([ToMelSpectrogram(), ToTensor()])

    dataset = AudioDataset(AUDIO_DIR, transform=transform)
    train_set, val_set = train_test_split(dataset, test_size=0.2) #, stratify=dataset.label)
    train_loader = DataLoader(dataset=train_set, batch_size=16, shuffle=True)
    val_loader = DataLoader(dataset=val_set, batch_size=16, shuffle=True)

    model = CoAtNet(num_classes=48)  # Assuming we have this class implemented following the paper or using a library
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=5e-4)
    criterion = nn.CrossEntropyLoss()

    num_epochs = 1100

    for epoch in range(num_epochs):
        model.train()
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            # Backward and optimize
            loss.backward()
            optimizer.step()

        print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item()}")

        # Validation
        if (epoch + 1) % 5 == 0:
            model.eval()
            with torch.no_grad():
                correct = 0
                total = 0
                for inputs, labels in val_loader:
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    outputs = model(inputs)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

                print(f"Validation Accuracy: {correct/total}")

    torch.save(model.state_dict(), MODEL_PATH)

def main():
    train()

if __name__ == "__main__":
    main()
