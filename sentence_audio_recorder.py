import threading
import time
import sounddevice as sd
import numpy as np
import wave
import yaml
from pynput import keyboard
import os
import scipy.io.wavfile as wav
from printout import switches, sent_instructions, keyboard_layout

# Define global variables
recording = False
keystrokes = []
audio_buffer = []
sample_rate = 44100  # Sample rate for audio recording

keyboard_sizes = {0: '100%_FullSize',
                  1: '96%_Compact',
                  2: '80%_Tenkeyless',
                  3: '75%_Compact_Tenkeyless',
                  4: '65%_Compact(Default for Macbooks)',
                  5: '60%_Mini',
                  6: 'Unk'}

def display_sizes():
    print("\nSelect a keyboard size by entering the corresponding index number:")
    for index, keysize in keyboard_sizes.items():
        print(f"{index}: {keysize}")

def display_switches(switches):
    print("\nSelect a switch by entering the corresponding index number:")
    for index, switch in switches.items():
        print(f"{index}: {switch}")

def get_user_input():
    global keyboard_name, keyboard_type, switch_color, keyboard_size
    keyboard_name = input("Enter the name of the keyboard: ")
    print("Select the type of keyboard:")
    print("1: Membrane")
    print("2: Mechanical")
    print("3: Magic Keyboard(Scissor) for Macs")
    keyboard_type_index = int(input("Enter the index of your choice: "))
    if keyboard_type_index == 1:
        keyboard_type = "membrane"
    elif keyboard_type_index == 2:
        keyboard_type = "mechanical"
        display_switches(switches)
        switch_color = switches[int(input("Enter the switch type index: "))]
    elif keyboard_type_index == 3:
        keyboard_type = "scissor"
    else:
        print("Invalid choice. Defaulting to membrane.")
        keyboard_type = "membrane"
    display_sizes()
    keyboard_size = keyboard_sizes[int(input("Enter the switch type index: "))]
    print("\n")
    print(keyboard_layout)
    print(sent_instructions)
    input("Press the ENTER key when ready. You will select a recording device now.")

def list_devices():
    devices = sd.query_devices()
    return devices

def select_device():
    devices = list_devices()
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")
    device_index = int(input("Select the recording device index: "))
    selected_device = devices[device_index]
    print(f"Selected device: {selected_device}")
    return device_index

# Function to handle audio callback
def audio_callback(indata, frames, time, status):
    global audio_buffer
    audio_buffer.append(indata.copy())

# Function to record audio
def record_audio(device, duration, filename, start_event, stop_event):
    global audio_buffer
    audio_buffer = []

    try:
        device_info = sd.query_devices(device, 'input')
        sample_rate = int(device_info['default_samplerate'])
        print(f"Using sample rate: {sample_rate}")

        stream = sd.InputStream(samplerate=sample_rate, channels=1, device=device, callback=audio_callback)
        with stream:
            stream.start()
            start_event.set()  # Signal that recording has started
            stop_event.wait(duration)  # Wait for the stop signal or timeout
            stream.stop()

        myrecording = np.concatenate(audio_buffer, axis=0)

        # Check and handle invalid values
        if not np.isfinite(myrecording).all():
            myrecording = np.nan_to_num(myrecording)
            print("Warning: Invalid values encountered in recording. Converted to zero.")

        wav.write(filename, sample_rate, np.int16(myrecording * 32767))
        print(f"record_audio saved sentence to {filename}")

    except Exception as e:
        print(f"An error occurred during recording: {e}")

# Function to handle key press events
def on_press(key):
    global recording, keystrokes, stop_event

    if key == keyboard.Key.esc:
        stop_event.set()
        recording = False
        return False  # Stop listener
    else:
        try:
            keystrokes.append(key.char)
        except AttributeError:
            keystrokes.append(str(key))

# Function to save keystrokes to a .yaml file
def save_keystrokes(filename):
    global keystrokes

    with open(filename, 'w') as file:
        yaml.dump({'keystrokes': keystrokes}, file)

# Function to ensure folder exists
def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

# Main function
def main():
    global recording, stop_event

    device_index = select_device()

    print('Waiting for recording thread to start')

    recording = True
    start_event = threading.Event()
    stop_event = threading.Event()
    current_time = int(time.time())
    ensure_folder_exists("data/sentence_data")
    filename = f"data/sentence_data/sentence_{current_time}.wav"


    audio_thread = threading.Thread(target=record_audio, args=(device_index, 30, filename, start_event, stop_event))
    audio_thread.start()
    start_event.wait()  # Wait for recording to start

    print("Please start typing. Press ESC to stop recording.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    stop_event.set()
    audio_thread.join()

    folder_path = "data/sentence_data"
    audio_filename = os.path.join(folder_path, f"sentence_{current_time}.wav")
    yaml_filename = os.path.join(folder_path, f"keystrokes_{current_time}.yaml")

    os.rename(filename, audio_filename)
    save_keystrokes(yaml_filename)

    print(f"Audio saved to {audio_filename}")
    print(f"Keystrokes saved to {yaml_filename}")

if __name__ == "__main__":
    main()
