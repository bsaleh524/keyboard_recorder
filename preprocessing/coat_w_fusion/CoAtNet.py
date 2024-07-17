import torch
from torch import nn

class CoAtNet_mech(nn.Module):
    def __init__(self, tabular_neurons=10, num_classes=36):
        super(CoAtNet_mech, self).__init__()

        # Convolutional part
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # Transformer part
        encoder_layer = nn.TransformerEncoderLayer(d_model=32, nhead=8)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=2)

        # Linear classifier
        # self.fc = nn.Linear(32, num_classes)

        ### Setup Tabular MLP
        self.tabular_ln4 = nn.Linear(tabular_neurons, 20)
        self.tabular_ln5 = nn.Linear(20, 20)
        self.tabular_ln6 = nn.Linear(20, 10)  # End of tabular
        self.relu = nn.ReLU()

        self.final_combo_ln = nn.Linear(42, num_classes)  # Combining classifier (32 + tabular(10))
        
        ### Setup final forward function to combine them

    def forward(self, img, tab):
        # Forward melspectrogram
        img = self.conv_layers(img)
        # Flattening
        img = img.view(img.size(0), -1, img.size(1))
        # Transformer encoder
        img = self.transformer_encoder(img)
        # Max pooling over time
        img, _ = torch.max(img, dim=1)  #TODO: What is the image size here?
        # Classifier
        # img = self.fc(img)

        ### Forward tabular data
        tab = self.tabular_ln4(tab)
        tab = self.relu(tab)
        tab = self.tabular_ln5(tab)
        tab = self.relu(tab)
        tab = self.tabular_ln6(tab)
        tab = self.relu(tab)

        ### New classifier
        x = torch.cat((img, tab), dim=1)
        x = self.relu(x)
        x = self.final_combo_ln(x)
        return  x
