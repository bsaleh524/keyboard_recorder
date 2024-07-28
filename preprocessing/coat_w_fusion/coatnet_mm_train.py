import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.transforms import Compose, ToTensor
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import librosa
import os
from coat_w_fusion.CoAtNet_mm import CoAtNet_multimodal
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
# Suppress specific warnings from librosa regarding depreciation
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning, module="librosa")

keyboard_dict = { # make lowercase
    0: '`', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: '-', 12: '=',
    13: 'q', 14: 'w', 15: 'e', 16: 'r', 17: 't', 18: 'y', 19: 'u', 20: 'i', 21: 'o', 22: 'p', 23: '[', 24: ']', 25:'bcksl',
    26: 'a', 27: 's', 28: 'd', 29: 'f', 30: 'g', 31: 'h', 32: 'j', 33: 'k', 34: 'l', 35: ';', 36: 'apost',
    37: 'z', 38: 'x', 39: 'c', 40: 'v', 41: 'b', 42: 'n', 43: 'm', 44: ',', 45: '.', 46: 'fwdsl', 47: 'space',
}
keyboard_reverse_map = {v: k for k, v in keyboard_dict.items()}
# Assume we have the following paths. Depend on your system, it could vary

# The following class help transform our input into mel-spectrogram
class ToMelSpectrogram:
    def __call__(self, samples):
        return librosa.feature.melspectrogram(samples, n_mels=64, win_length=1024, hop_length=500)


# This class is to load audio data and apply the transformation
class AudioDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir, pickle_file, transform=None):
        # self.data_dir = data_dir
        self.image_dir = data_dir
        self.transform = transform
        # self.file_list = os.listdir(self.image_dir)
        self.tabular = pd.read_pickle(pickle_file)
        self.tabular_neurons = len(self.tabular.columns)

    def __len__(self):
        # return len(self.file_list)
        return len(self.tabular)

    def __getitem__(self, idx):
        # ensures we select indexing rows of the dataframe
        if torch.is_tensor(idx):
            idx = idx.tolist()

        # Acquire entire row per index asked for by batch
        tabular = self.tabular.iloc[idx, 0:]  # get everything
        filename = tabular['audio_file'] # grab audiofile name

        #Process audio data
        waveform, _ = librosa.load(os.path.join(self.image_dir, filename), #self.file_list[idx]),
                                   sr=None,
                                   duration=1.0,
                                   mono=True)

        # label_char = self.file_list[idx].split("_")[2]  # Assuming the file name is 'label_otherInfo.wav'
        label_char = filename.split("_")[2]
        
        # Encode the label using char_to_idx dictionary
        label = keyboard_reverse_map[label_char]

        if self.transform:
            waveform = self.transform(waveform)

        # Grab remaining tabular data
        tabular = tabular.drop(['audio_file'])
        tabular = tabular.tolist()
        tabular = torch.FloatTensor(tabular)

        return waveform, tabular, label


def train(audio_dir,
          tabular_pkl_file,
          model_path,
          num_classes=48,
          batch_size=16,
          split_size=0.2,
          epochs=1100):
    # We will use the transformation to convert the audio into Mel spectrogram
    transform = Compose([ToMelSpectrogram(), ToTensor()])

    # Load in Audiodataset and split
    dataset = AudioDataset(audio_dir, pickle_file=tabular_pkl_file, transform=transform)
    train_set, val_set = train_test_split(dataset, test_size=split_size) #, stratify=dataset.label)
    train_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(dataset=val_set, batch_size=batch_size, shuffle=True)

    # Load in CoATNet model
    # Assuming we have this class implemented following the paper or using a library
    model = CoAtNet_multimodal(tabular_neurons=dataset.tabular_neurons,
                               num_classes=num_classes
    )
    model = model.to(device)

    # 
    optimizer = optim.Adam(model.parameters(), lr=5e-4)
    criterion = nn.CrossEntropyLoss()

    #
    num_epochs = epochs #1100


    for epoch in range(num_epochs):
        model.train()
        for images, tabular, labels in train_loader:
            images = images.to(device)
            tabular = tabular.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            # Forward pass
            outputs = model(images, tabular)
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
                for images, tabular, labels in val_loader:
                    images = images.to(device)
                    tabular = tabular.to(device)
                    labels = labels.to(device)

                    outputs = model(images, tabular)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

                print(f"Validation Accuracy: {correct/total}")

    torch.save(model.state_dict(), model_path)
    return model.state_dict()

if __name__ == "__main__":
    AUDIO_DIR = 'preprocessed_data/'
    TABULAR_FILE = 'preprocessed_data/keyboard_tabular_data.pkl'
    MODEL_PATH = 'models/model.pt'

    train(audio_dir=AUDIO_DIR,
          tabular_pkl_file=TABULAR_FILE,
          model_path=MODEL_PATH,
          batch_size=16,
          split_size=0.2,
          num_classes=48)
