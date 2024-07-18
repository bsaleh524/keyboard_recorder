import numpy as np
import librosa
import soundfile as sf
import os

def calculate_energy(y, sr):
    # Perform STFT
    stft_result = np.abs(librosa.stft(y))
    
    # Calculate energy
    energy = np.sum(stft_result**2, axis=0)
    
    # Normalize energy
    energy = energy / np.max(energy)
    
    return energy

def extract_keystrokes(audio_path, threshold, output_dir):
    # Load audio file
    y, sr = librosa.load(audio_path, sr=None)
    
    # Calculate energy
    energy = calculate_energy(y, sr)
    
    # Detect keystrokes
    keystroke_indices = np.where(energy > threshold)[0]
    
    # Group keystroke indices
    keystroke_groups = []
    if len(keystroke_indices) > 0:
        current_group = [keystroke_indices[0]]
        for i in range(1, len(keystroke_indices)):
            if keystroke_indices[i] - keystroke_indices[i-1] > 1:  # assuming keystrokes are at least one frame apart
                keystroke_groups.append(current_group)
                current_group = [keystroke_indices[i]]
            else:
                current_group.append(keystroke_indices[i])
        keystroke_groups.append(current_group)
    
    # Save individual keystroke audio files
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, group in enumerate(keystroke_groups):
        # Find the center of the group
        center_index = np.mean(group).astype(int)
        
        # Ensure both peaks are included
        start_frame = max(0, group[0] - 1)  # Start a bit earlier
        end_frame = min(len(energy), group[-1] + 1)  # End a bit later
        
        start_sample = librosa.frames_to_samples(start_frame)
        end_sample = librosa.frames_to_samples(end_frame + 1)
        
        keystroke_audio = y[start_sample:end_sample]
        output_path = os.path.join(output_dir, f'keystroke_{i}.wav')
        sf.write(output_path, keystroke_audio, sr)
        print(f'Saved keystroke {i} to {output_path}')

# Example usage
audio_path = 'twentyfive_recorder/E_25_presses_modified.wav'
threshold = 0.1  # Adjust this threshold based on your data
output_dir = 'keystrokes'

# Extract keystrokes with the chosen threshold
extract_keystrokes(audio_path, threshold, output_dir)
