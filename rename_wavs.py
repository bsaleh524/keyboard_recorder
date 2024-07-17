import os
import shutil

def rename_and_copy_files(base_folder, file_extensions, preprocessed_folder):
    # Ensure the preprocessed folder exists
    if not os.path.exists(preprocessed_folder):
        os.makedirs(preprocessed_folder)
    
    # Get all user directories
    user_dirs = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
    
    for user in user_dirs:
        if 'Keystroke' in user:
            continue
        user_folder = os.path.join(base_folder, user)
        
        # Process both key_data and sentence_data folders
        for data_type in ['key_data']: #, 'sentence_data']:
            data_folder = os.path.join(user_folder, 'data', data_type)
            if os.path.exists(data_folder):
                for file_name in os.listdir(data_folder):
                    for ext in file_extensions:
                        if file_name.endswith(ext):
                            old_path = os.path.join(data_folder, file_name)
                            if user not in file_name:
                                new_file_name = f"{file_name.split(ext)[0]}_{user}{ext}"
                                new_path = os.path.join(data_folder, new_file_name)
                                os.rename(old_path, new_path)
                                print(f"Renamed: {old_path} -> {new_path}")
                                old_path = new_path  # Update old_path to new_path for copying
                            # Copy .wav files to preprocessed folder
                            if ext == '.wav':
                                dest_path = os.path.join(preprocessed_folder, file_name)
                                if os.path.exists(dest_path):
                                    file_base, file_ext = os.path.splitext(file_name)
                                    dest_path = os.path.join(preprocessed_folder, f"{file_base}_{user}{file_ext}")
                                shutil.copy2(old_path, dest_path)
                                print(f"Copied: {old_path} -> {dest_path}")

# Set the base folder path where the user folders are located
base_folder_path = 'data'
# List of file extensions to rename and copy
file_extensions = ['.wav', '.yaml']
# Set the destination folder for preprocessed .wav files
preprocessed_folder_path = 'preprocessed_data'
rename_and_copy_files(base_folder_path, file_extensions, preprocessed_folder_path)
