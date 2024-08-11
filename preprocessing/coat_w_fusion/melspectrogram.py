import librosa

# The following class help transform our input into mel-spectrogram
class ToMelSpectrogram:
    def __call__(self, samples):
        return librosa.feature.melspectrogram(samples, n_mels=64, win_length=1024, hop_length=500)