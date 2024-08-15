import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.transforms import ToTensor
from coat_w_fusion.melspectrogram import ToMelSpectrogram
from coat_w_fusion.CoAtNet_mm import CoAtNet_multimodal
from coat_w_fusion.audio_dataset import AudioDataset

# assuming model and transform functions are already defined
# and 'MODEL_PATH' contains the path to the trained model 

# class PredictDataset(torch.utils.data.Dataset):
#     def __init__(self, audio_paths, transform=None):
#         self.audio_paths = audio_paths
#         self.transform = transform

#     def __len__(self):
#         return len(self.audio_paths)

#     def __getitem__(self, idx):
#         audio_path = self.audio_paths[idx]
#         audio_clip = load_audio_clip(audio_path)

#         if self.transform:
#             audio_clip = self.transform(audio_clip)

#         return audio_clip

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

def load_model(path,
               tabular_neurons,
               num_classes):
    model = CoAtNet_multimodal(tabular_neurons=tabular_neurons,
                               num_classes=num_classes
    )
      # should match the architecture of the trained model
    model.load_state_dict(torch.load(path))
    model.eval()
    return model


def predict(audio_dir,
            model_path,
            experiment='1',):

    transform = transforms.Compose([
        ToMelSpectrogram(), ToTensor()  # add transforms that were used while training
    ])
    tabular_pkl_file = audio_dir + 'keyboard_tabular_data.pkl'
    # dataset = PredictDataset(audio_dir, transform=transform)
    dataset = AudioDataset(audio_dir,
                           pickle_file=tabular_pkl_file,
                           transform=transform,
                           desired_experiment=experiment)
    
    data_loader = DataLoader(dataset, batch_size=1, shuffle=False)
    dataset_num_classes = len(dataset.keyboard_map.keys())
    model = load_model(model_path,
                       tabular_neurons=dataset.tabular_neurons,
                        num_classes=dataset_num_classes
    )

    predictions = []

    for images, tabular, labels in data_loader:

        # batch = batch.cuda()
        outputs = model(images, tabular)
        _, predicted = torch.max(outputs.data, 1)  # change if multi-label classification
        predictions.append((predicted.item(), labels.item()))

    return predictions

def main():
    audio_dir = "../preprocessed_data/"  # replace with actual paths
    model_path = "../models/model_exp3.pt"
    experiment_num = '1'
    predictions = predict(audio_dir=audio_dir,
                          model_path=model_path,
                          experiment=experiment_num)
    print(predictions)

if __name__ == "__main__":
    main()
