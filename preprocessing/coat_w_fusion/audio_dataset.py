import torch
import pandas as pd
import librosa
import os
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
# Suppress specific warnings from librosa regarding depreciation
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


keyboard_dict = { # make lowercase
    0: '`', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: '-', 12: '=',
    13: 'q', 14: 'w', 15: 'e', 16: 'r', 17: 't', 18: 'y', 19: 'u', 20: 'i', 21: 'o', 22: 'p', 23: '[', 24: ']', 25:'bcksl',
    26: 'a', 27: 's', 28: 'd', 29: 'f', 30: 'g', 31: 'h', 32: 'j', 33: 'k', 34: 'l', 35: ';', 36: 'apost',
    37: 'z', 38: 'x', 39: 'c', 40: 'v', 41: 'b', 42: 'n', 43: 'm', 44: ',', 45: '.', 46: 'fwdsl', 47: 'space',
}
keyboard_reverse_map = {v: k for k, v in keyboard_dict.items()}

h_dict = {0: 'noth', 1: 'h',}
h_reverse_map = {v: k for k, v in h_dict.items()}

space_dict = {0: 'notspace', 1: 'space',}
space_reverse_map = {v: k for k, v in space_dict.items()}


experiment_dict = {'1': keyboard_reverse_map,
                   '2': keyboard_reverse_map,
                   '3': h_reverse_map,
                   '4': h_reverse_map,
                   '5': space_reverse_map,}

# Assume we have the following paths. Depend on your system, it could vary

# This class is to load audio data and apply the transformation
class AudioDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir, pickle_file,
                 transform=None, desired_experiment='1'):
        # self.data_dir = data_dir
        self.image_dir = data_dir
        self.transform = transform
        # self.file_list = os.listdir(self.image_dir)
        self.tabular = pd.read_pickle(pickle_file)
        self.tabular_neurons = len(self.tabular.columns) - 1  # Subtract away audio file name
        self.keyboard_map = experiment_dict[desired_experiment]

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
        label = self.keyboard_map[label_char]

        if self.transform:
            waveform = self.transform(waveform)

        # Grab remaining tabular data
        tabular = tabular.drop(['audio_file'])
        tabular = tabular.tolist()
        tabular = torch.FloatTensor(tabular)

        return waveform, tabular, label