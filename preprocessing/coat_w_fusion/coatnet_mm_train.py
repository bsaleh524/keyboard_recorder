import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.transforms import Compose, ToTensor
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from coat_w_fusion.CoAtNet_mm import CoAtNet_multimodal
from coat_w_fusion.audio_dataset import AudioDataset
from coat_w_fusion.melspectrogram import ToMelSpectrogram
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
# Suppress specific warnings from librosa regarding depreciation
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)



def train(audio_dir,
          tabular_pkl_file,
          model_path,
          experiment='1',
          batch_size=16,
          split_size=0.2,
          learn_rate=5e-4,
          epochs=1100):
    # We will use the transformation to convert the audio into Mel spectrogram
    transform = Compose([ToMelSpectrogram(), ToTensor()])

    # Load in Audiodataset and split
    dataset = AudioDataset(audio_dir,
                           pickle_file=tabular_pkl_file,
                           transform=transform,
                           desired_experiment=experiment)
    dataset_num_classes = len(dataset.keyboard_map.keys())
    train_set, val_set = train_test_split(dataset, test_size=split_size) #, stratify=dataset.label)
    train_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(dataset=val_set, batch_size=batch_size, shuffle=True)

    # Load in CoATNet model
    # Assuming we have this class implemented following the paper or using a library
    model = CoAtNet_multimodal(tabular_neurons=dataset.tabular_neurons,
                               num_classes=dataset_num_classes
    )
    model = model.to(device)

    # 
    optimizer = optim.Adam(model.parameters(), lr=learn_rate)
    criterion = nn.CrossEntropyLoss()

    #
    num_epochs = epochs #1100

    training_losses = []
    validation_losses = []

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

        training_losses.append(loss.item())
        
        # Validation
        model.eval()
        with torch.no_grad():
            correct = 0
            total = 0
            for images, tabular, labels in val_loader:
                images = images.to(device)
                tabular = tabular.to(device)
                labels = labels.to(device)

                outputs = model(images, tabular)
                val_loss = criterion(outputs, labels)###Finish this

                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        # print(f'correct/total:{correct}/{total} = {correct/total}')
        val_acc = correct/total
        validation_losses.append(val_loss.item())
        print(f"Epoch [{epoch + 1}/{num_epochs}] || Train Loss: {training_losses[-1]:.4f} || Val Loss: {validation_losses[-1]:.4f} || Val Accuracy: {val_acc:.4f}")

    torch.save(model.state_dict(), model_path)
    return model.state_dict(), training_losses, validation_losses, val_acc

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
