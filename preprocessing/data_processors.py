import numpy as np
import pandas as pd
import librosa
import os
import yaml
import matplotlib.pyplot as plt
import soundfile as sf
import shutil
from sklearn.preprocessing import LabelEncoder
import glob

microphone_mapper = {'Mic/Inst (Samson G-Track Pro)': 'Samson_GTrack_Pro',
                        'Microphone (3- USB PnP Audio De': 'GenericPnP'}
material_mapper = {'dropctrlv1': 'aluminum',
                'keychronq3': 'aluminum',
                'macbookprom1': 'aluminum',
                'dell_keyboard': 'plastic'}

unnecessary_cols = ['default_high_input_latency',
                'default_high_output_latency',
                'default_low_input_latency',
                'default_low_output_latency',
                'default_samplerate',
                'hostapi',
                'index',
                'max_input_channels',
                'max_output_channels',
                'timestamp',]
keyboard_sizes = {
    '100%_FullSize': 5,
    '96%_Compact': 4,
    '80%_Tenkeyless': 3,
    '75%_Compact_Tenkeyless': 2,
    '65%_Compact(Default for Macbooks)': 1,
    '60%_Mini': 0,
}

switches_dict = {
    'Clicky': [
        'Cherry MX Blue', 'Cherry MX Green', 'Cherry MX White',
        'Gateron Blue', 'Gateron Green',
    ],
    'Tactile': [
        'Cherry MX Brown', 'Cherry MX Clear',
        'Gateron Brown', 'Halo True', 'Halo Clear',
    ],
    'Linear': [
        'Cherry MX Red', 'Cherry MX Black', 'Cherry MX Silent Red', 'Cherry MX Speed Silver',
        'Gateron Red', 'Gateron Black', 'Gateron Silent Red', 'Gateron Yellow',
        'Cherry MX Grey', 'Gateron Clear', 'Gateron White',
    ],
    'None': ['None']
}


def old_data_processing(data_folder='../data/old_data/',
                        output_dir='../preprocessed_data/'):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)  # Delete the folder and its contents
    os.makedirs(output_dir)

    # Initialize an empty list to store the data
    key_data_list = []

    # Loop through all user folders in the data folder
    for user_folder in os.listdir(data_folder):
        if 'Keystroke' in user_folder:
            continue
        user_folder_path = os.path.join(data_folder, user_folder)
        if os.path.isdir(user_folder_path):  # Check if it's a directory
            key_folder_path = os.path.join(user_folder_path, 'data', 'key_data')

            # Key data, then sentence data
            # for internal_folder in [key_folder_path, sentence_folder_path]:
            for file_name in os.listdir(key_folder_path):
                # key_folder_path = os.path.join(data_folder, user_folder)
                # Check if the file is a YAML file
                if file_name.endswith('.yaml'):
                    # Extract key_pressed value from the filename
                    key_pressed = file_name.split('_')[2]
                    
                    # Construct the full path to the YAML file
                    yaml_file_path = os.path.join(key_folder_path, file_name)
                    
                    # Read the YAML file and filter out the 'key_pressed' field and subsequent lines until 'keyboard_name'
                    with open(yaml_file_path, 'r') as file:
                        lines = file.readlines()
                    
                    filtered_lines = []
                    skip = False
                    for line in lines:
                        if line.strip().startswith('key_pressed:'):
                            skip = True
                        if skip and line.strip().startswith('keyboard_name:'):
                            skip = False
                        if not skip:
                            filtered_lines.append(line)
                    
                    # Load the filtered lines into a dictionary
                    yaml_data = yaml.safe_load(''.join(filtered_lines))
                    
                    # Add the user, audio file name, and key_pressed information
                    yaml_data['user'] = user_folder
                    # yaml_data['audio_file'] = file_name.replace('.yaml', f'_{user_folder}.wav')
                    # original_file = file_name.replace('.yaml', '.wav')
                    yaml_data['audio_file'] = file_name.replace('.yaml', '.wav') # Assuming audio files are in .wav format
                    yaml_data['key_pressed'] = key_pressed

                    # Copy the audio file to the output directory
                    original_audio_file = yaml_data['audio_file']
                    new_audio_file_name = original_audio_file.replace('.wav', f'_{user_folder}.wav')
                    source_audio_file_path = os.path.join(key_folder_path, original_audio_file)
                    destination_audio_file_path = os.path.join(output_dir, new_audio_file_name)
                    shutil.copy2(source_audio_file_path, destination_audio_file_path)
                    yaml_data['audio_file'] = new_audio_file_name
                    key_data_list.append(yaml_data)

    # Convert the list of dictionaries to a DataFrame
    key_df = pd.DataFrame(key_data_list)
    return key_df


def calculate_energy(y, sr):
    stft_result = np.abs(librosa.stft(y))
    energy = np.sum(stft_result**2, axis=0)
    energy = energy / np.max(energy)
    return energy

def sliding_window_average(energy, window_size):
    averaged_energy = np.convolve(energy, np.ones(window_size)/window_size, mode='same')
    return averaged_energy

def get_yaml_file(folder_path):
    for file in os.listdir(folder_path):
        if (file.endswith(".yaml") or file.endswith(".yml")):
            yaml_file_path = os.path.join(folder_path, file)
            # Get all yaml data first
            # Read the YAML file and filter out the 'key_pressed' field and subsequent lines until 'keyboard_name'
            with open(yaml_file_path, 'r') as file:
                lines = file.readlines()
            
            # Load the filtered lines into a dictionary
            yaml_data = yaml.safe_load(''.join(lines))
            
            # Add the user, audio file name, and key_pressed information
            user_keyboard_name = yaml_data['keyboard_name']
            user_keyboard_size = yaml_data['keyboard_size']
            keyboard_type = yaml_data['keyboard_type']
            switch_color = yaml_data['switch_color']
            return user_keyboard_name, user_keyboard_size, keyboard_type, switch_color
    return None

def extract_keystrokes(data_folder='../data/new_data/',
                       low_threshold=0.005,
                       high_threshold=0.01,
                       output_dir='../preprocessed_data/',
                       window_size=35,
                       target_duration=1.0,
                       give_plot=False,
                       debug=False):
    
    for user_folder in os.listdir(data_folder):
        if 'Keystroke' in user_folder:
            continue
        user_folder_path = os.path.join(data_folder, user_folder)
        audio_data = []
        if os.path.isdir(user_folder_path):  # Check if it's a directory
            key_folder_path = os.path.join(user_folder_path, 'key_data')
            user_keyboard_name, user_keyboard_size, keyboard_type, switch_color = get_yaml_file(key_folder_path)
            if not key_folder_path:
                raise('Yaml file for data not found')

            for file_name in os.listdir(key_folder_path):
                if file_name.endswith('.yaml'):
                    continue
                        
                elif file_name.endswith('.wav'):
                    # Wav file
                    key_pressed = file_name.split('_')[2].lower()

                    wav_file_path = os.path.join(key_folder_path, file_name)

                    y, sr = librosa.load(wav_file_path, sr=None)
                    energy = calculate_energy(y, sr)
                    averaged_energy = sliding_window_average(energy, window_size)
                    
                    keystroke_indices = np.where(averaged_energy > low_threshold)[0]
                    
                    keystroke_events = []
                    if len(keystroke_indices) > 0:
                        start_idx = keystroke_indices[0]
                        for i in range(1, len(keystroke_indices)):
                            if keystroke_indices[i] - keystroke_indices[i-1] > 1:
                                end_idx = keystroke_indices[i-1]
                                keystroke_events.append((start_idx, end_idx))
                                start_idx = keystroke_indices[i]
                        keystroke_events.append((start_idx, keystroke_indices[-1]))
                    
                    filtered_keystroke_events = []
                    for start_frame, end_frame in keystroke_events:
                        if np.max(averaged_energy[start_frame:end_frame]) > high_threshold:
                            length = end_frame - start_frame
                            extension = int(0.1 * length)
                            start_frame = max(0, start_frame - extension)
                            end_frame = min(len(averaged_energy), end_frame + extension)
                            filtered_keystroke_events.append((start_frame, end_frame))
                    
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    
                    for i, (start_frame, end_frame) in enumerate(filtered_keystroke_events[1:]):
                        start_sample = librosa.frames_to_samples(start_frame)
                        end_sample = librosa.frames_to_samples(end_frame + 1)
                        
                        keystroke_audio = y[start_sample:end_sample]
                        
                        # Calculate required padding
                        target_samples = int(target_duration * sr)
                        current_samples = len(keystroke_audio)
                        padding_needed = target_samples - current_samples
                        if padding_needed > 0:
                            pad_before = padding_needed // 2
                            pad_after = padding_needed - pad_before
                            keystroke_audio = np.pad(keystroke_audio, (pad_before, pad_after), 'constant')
                        
                        output_path = os.path.join(output_dir, f'key_press_{key_pressed}_{i}_{user_folder}.wav')
                        sf.write(output_path, keystroke_audio, sr)
                        if debug:
                            print(f'Saved keystroke {i} to {output_path}')
                        
                        # Write the filename and additional data to a dataframe.
                        audio_data.append([user_keyboard_name,
                                           user_keyboard_size, 
                                           keyboard_type,
                                           switch_color,
                                           f'key_press_{key_pressed}_{i}_{user_folder}.wav',
                                           key_pressed])

                    if give_plot:
                        # Plot for visualization
                        time = np.linspace(0, len(y) / sr, len(y))
                        frames_time = np.linspace(0, len(energy) * window_size / sr, len(energy))
                        
                        plt.figure(figsize=(15, 7))
                        # plt.plot(time, y, label='Audio Signal')
                        plt.plot(frames_time, averaged_energy, label='Averaged Energy', color='orange')
                        plt.axhline(y=low_threshold, color='black', linestyle=':', label='Low Threshold')
                        plt.axhline(y=high_threshold, color='green', linestyle=':', label='High Threshold')
                        for start_frame, end_frame in filtered_keystroke_events[1:]:
                            plt.axvline(x=start_frame * window_size / sr, color='red', linestyle='-', linewidth=0.2)
                            plt.axvline(x=end_frame * window_size / sr, color='magenta', linestyle='-', linewidth=0.2)
                        plt.xlabel('Time (s)')
                        plt.ylabel('Amplitude / Averaged Energy')
                        plt.legend()
                        plt.title('Keystroke Detection Visualization')
                        plt.show()
    key_df = pd.DataFrame(data=audio_data, columns=['keyboard_name', 'keyboard_size', 'keyboard_type',
                                                    'switch_color', 'audio_file', 'key_pressed'])
    return key_df

def map_switch_type(switch):
    for key, values in switches_dict.items():
        if switch in values:
            return key
    print(f"{switch} was not in any category. setting to NA")
    return 'NA'  # If switch doesn't match any category

def make_tabular_file(df, output_dir, ignore_check=False):
    len_of_output_wavs = len(glob.glob(f'{output_dir}*.wav'))
    len_of_df = df.shape[0]
    if ignore_check:
        path_to_pkl = f'{output_dir}keyboard_tabular_data.pkl'
        df.to_pickle(path_to_pkl)
        return path_to_pkl
    else:
        if len_of_df == len_of_output_wavs:
            print(f'Matching shapes. Outputting tabular pickle file.')
            path_to_pkl = f'{output_dir}keyboard_tabular_data.pkl'
            df.to_pickle(path_to_pkl)
        else:
            print(f'shape of df: {len_of_df}')
            print(f'shape of len(glob.glob(output_dir/*.wav)): {len_of_output_wavs}')
            raise('Error: Directory files are not the same length as the dataframe!')
        return path_to_pkl

def combine_for_train_and_test(all_dataframes: list,
                               output_dir='../preprocessed_data/'):

    # Combine dataframes into one.
    combined_key_df = pd.concat(all_dataframes, ignore_index=True)
    combined_key_df.head()

    # Add keyboard material column
    combined_key_df['keyboard_name'] = combined_key_df['keyboard_name'].apply(lambda x: x.lower().replace(" ", ""))
    combined_key_df['keyboard_material'] = combined_key_df['keyboard_name'].map(material_mapper)
    combined_key_df.drop('keyboard_name', axis=1, inplace=True)
    
    # Add Keyboard Microphone Column cleanup
    combined_key_df['name'].unique()
    combined_key_df['microphone'] = combined_key_df['name'].map(microphone_mapper)
    combined_key_df.drop('name', axis=1, inplace=True)

    # Drop unneeded columns
    combined_key_df.drop(unnecessary_cols, axis=1, inplace=True)

    # One-hot Encoding
    ## Ordinally encode 'keyboard_size' column
    combined_key_df['keyboard_size'] = combined_key_df['keyboard_size'].map(keyboard_sizes)

    combined_key_df['switch_type'] = combined_key_df['switch_color'].map(lambda x: map_switch_type(x))
    combined_key_df.drop(['switch_color'], axis=1, inplace=True)

    # Get dummies on dataframe
    combined_key_df = pd.get_dummies(combined_key_df, columns=['switch_type', 'keyboard_material'])

    # label encode y labels
    le_key_pressed = LabelEncoder()
    combined_key_df['key_pressed'] = le_key_pressed.fit_transform(combined_key_df['key_pressed'])

    # Final droppings
    combined_key_df.drop(['user', 'microphone', 'keyboard_type', 'key_pressed'], axis=1, inplace=True)

    # Drop material(for now)
    combined_key_df.drop(['keyboard_material_aluminum'], axis=1, inplace=True)

    ### Create pkl file
    print(f"Number of tabular items: {combined_key_df.shape[0]}")
    print(f"Number of audio files in the folder: {len(glob.glob(f'{output_dir}*.wav'))}")

    path_to_pkl = make_tabular_file(df=combined_key_df, output_dir=output_dir)
    
    return combined_key_df, path_to_pkl

def create_experiments(processed_data, path_to_pkl):

    experiment_folders = [f'{processed_data}experiment_1/',
                   f'{processed_data}experiment_2/',
                   f'{processed_data}experiment_3/',
                   f'{processed_data}experiment_4/',
                   f'{processed_data}experiment_5/',]
    
    # read in tabular data to know what files are which
    df = pd.read_pickle(path_to_pkl)

    for exp_folder in experiment_folders:
        if os.path.exists(exp_folder):
            shutil.rmtree(exp_folder)  # Delete the folder and its contents
        os.makedirs(exp_folder)
    
    ###### Experiment 1: Copy preprocessed folder to experiment 1 folder. All data + classes
    # Loop through the source folder
    for filename in os.listdir(processed_data):
        # Check for .wav and .pkl files
        if filename.endswith('.wav') or filename.endswith('.pkl'):
            # Construct full file path
            file_path = os.path.join(processed_data, filename)
            # Copy the file to the destination folder
            shutil.copy(file_path, experiment_folders[0])
    print(f'Generated Experiment #{experiment_folders[0][-2]} at {experiment_folders[0]}')
    ######


    ###### Experiment 2: User1 Only dataset(DropCTRLV1 Tactile Keys). All Classes
    experiment_2_df = df.copy(deep=True)
    experiment_2_df = experiment_2_df[experiment_2_df['audio_file'].str.contains('User1')]
    
    for audio_file in experiment_2_df['audio_file']:
        source_path = os.path.join(processed_data, audio_file)
        destination_path = os.path.join(experiment_folders[1], audio_file)
        shutil.copy2(source_path, destination_path)
    
    # # Copy over pkl file
    path_to_pkl = make_tabular_file(df=experiment_2_df, output_dir=experiment_folders[1])
    print(f'Generated Experiment #{experiment_folders[1][-2]} at {experiment_folders[1]}')

    ###### Experiment 3: Binary classification. Predict only 'h' with all datasets
    experiment_3_df = df.copy(deep=True)
    key_to_predict = 'h'

    # Loop through the source folder
    for idx, audio_file in enumerate(experiment_3_df['audio_file']):
        current_label = audio_file.split("_")[2]
        if current_label == key_to_predict:
            # if it is, copy it normally
            new_audio_file = audio_file
        else:
            new_audio_file = audio_file.replace(
                f"_{current_label}_", f'_noth_{idx}_')

        experiment_3_df.at[idx, 'audio_file'] = new_audio_file

        # Construct full file path
        file_path = os.path.join(processed_data, audio_file)
        new_file_path = os.path.join(experiment_folders[2], new_audio_file)
        # Copy the file to the destination folder
        shutil.copy(file_path, new_file_path)
        # print(f'Copied {filename} to {experiment_folders[0]}')
    
    # # Copy over pkl file
    path_to_pkl = make_tabular_file(df=experiment_3_df, output_dir=experiment_folders[2])
    print(f'Generated Experiment #{experiment_folders[2][-2]} at {experiment_folders[2]}')

    ###### Experiment 4: Binary classification. Predict only 'h' with only Drop dataset
    experiment_4_df = df.copy(deep=True)
    experiment_4_df = experiment_4_df[
        experiment_4_df['audio_file'].str.contains('User1')
    ].reset_index()
    key_to_predict = 'h'

    # Loop through the source folder
    for idx, audio_file in enumerate(experiment_4_df['audio_file']):
        current_label = audio_file.split("_")[2]
        if current_label == key_to_predict:
            # if it is, copy it normally
            new_audio_file = audio_file
        else:
            new_audio_file = audio_file.replace(
                f"_{current_label}_", f'_noth_{idx}_')

        experiment_4_df.at[idx, 'audio_file'] = new_audio_file

        # Construct full file path
        file_path = os.path.join(processed_data, audio_file)
        new_file_path = os.path.join(experiment_folders[3], new_audio_file)
        # Copy the file to the destination folder
        shutil.copy(file_path, new_file_path)
        # print(f'Copied {filename} to {experiment_folders[0]}')
    
    # # Copy over pkl file
    path_to_pkl = make_tabular_file(df=experiment_4_df,
                                    output_dir=experiment_folders[3],
                                    ignore_check=True)
    print(f'Generated Experiment #{experiment_folders[3][-2]} at {experiment_folders[3]}')


    ###### Experiment 5: Binary classification. Predict only 'space' with only Drop dataset
    experiment_5_df = df.copy(deep=True)
    experiment_5_df = experiment_5_df[
        experiment_5_df['audio_file'].str.contains('User1')
    ].reset_index()
    key_to_predict = 'space'

    # Loop through the source folder
    for idx, audio_file in enumerate(experiment_5_df['audio_file']):
        current_label = audio_file.split("_")[2]
        if current_label == key_to_predict:
            # if it is, copy it normally
            new_audio_file = audio_file
        else:
            new_audio_file = audio_file.replace(
                f"_{current_label}_", f'_notspace_{idx}_')

        experiment_5_df.at[idx, 'audio_file'] = new_audio_file

        # Construct full file path
        file_path = os.path.join(processed_data, audio_file)
        new_file_path = os.path.join(experiment_folders[4], new_audio_file)
        # Copy the file to the destination folder
        shutil.copy(file_path, new_file_path)
        # print(f'Copied {filename} to {experiment_folders[0]}')
    
    # # Copy over pkl file
    path_to_pkl = make_tabular_file(df=experiment_5_df,
                                    output_dir=experiment_folders[4],
                                    ignore_check=True)
    print(f'Generated Experiment #{experiment_folders[4][-2]} at {experiment_folders[4]}')
    
    return experiment_folders, df, experiment_2_df, \
        experiment_3_df, experiment_4_df, experiment_5_df