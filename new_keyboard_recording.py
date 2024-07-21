import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading
import yaml
import os

# Parameters for audio recording
sample_rate = 44100  # Sample rate in Hz
recording_duration = 1.5  # Duration to record after each key press in seconds
number_of_recordings = 10
stop_event = threading.Event()
audio_buffer = []
recording_device_info = {}

keyboard_dict = {  # make lowercase
    0: '`', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: '-', 12: '=',
    13: 'q', 14: 'w', 15: 'e', 16: 'r', 17: 't', 18: 'y', 19: 'u', 20: 'i', 21: 'o', 22: 'p', 23: '[', 24: ']', 25: '\\',
    26: 'a', 27: 's', 28: 'd', 29: 'f', 30: 'g', 31: 'h', 32: 'j', 33: 'k', 34: 'l', 35: ';', 36: '\'',
    37: 'z', 38: 'x', 39: 'c', 40: 'v', 41: 'b', 42: 'n', 43: 'm', 44: ',', 45: '.', 46: '/', 47: keyboard.Key.space,
}
forbidden_keys = {'\\': 'bcksl', '\'': 'apost', '/': 'fwdsl', keyboard.Key.space: "space"}

# Global variables to keep track of state
recording = False
key_log = []
current_key = None

def reorder_keyboard_dict(start_key):
    items = list(keyboard_dict.items())
    start_index = items.index((start_key, keyboard_dict[start_key]))
    reordered_items = items[start_index:] + items[:start_index]
    reordered_dict = dict(reordered_items)
    return reordered_dict

def remove_keys_before_start_key(start_key):
    items = list(keyboard_dict.items())
    start_index = items.index((start_key, keyboard_dict[start_key]))
    remaining_items = items[start_index:]
    remaining_dict = dict(remaining_items)
    return remaining_dict

def list_devices():
    devices = sd.query_devices()
    return devices

def select_device():
    global recording_device_info
    devices = list_devices()
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")
    device_index = int(input("Select the recording device index: "))
    recording_device_info = {micinfo: devices[device_index][micinfo] for micinfo in devices[device_index].keys()}
    return device_index

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_buffer.extend(indata.copy())

def record_audio(device, duration, filename, start_event, stop_event):
    global audio_buffer
    audio_buffer = []

    stream = sd.InputStream(samplerate=sample_rate, channels=1, device=device, callback=audio_callback)
    with stream:
        stream.start()
        start_event.set()  # Signal that recording has started
        stop_event.wait(duration)  # Wait for the stop signal or timeout
        time.sleep(1)
        stream.stop()

    myrecording = np.array(audio_buffer)

    # Check and handle invalid values
    if not np.isfinite(myrecording).all():
        myrecording = np.nan_to_num(myrecording)
        print("Warning: Invalid values encountered in recording. Converted to zero.")

    wav.write(filename, sample_rate, np.int16(myrecording * 32767))
    print(f"Audio saved to {filename}")

def save_yaml(filename, key_pressed, timestamp, keyboard_name, keyboard_type, switch_color, keyboard_size):
    data = {
        'keyboard_name': keyboard_name,
        'keyboard_type': keyboard_type,
        'keyboard_size': keyboard_size,
        'switch_color': switch_color if keyboard_type.lower() == 'mechanical' else None,
        'key_pressed': key_pressed,
        'timestamp': timestamp
    }
    data.update(recording_device_info)
    yaml_filename = filename.replace('.wav', '.yaml')
    with open(yaml_filename, 'w') as yaml_file:
        yaml.dump(data, yaml_file)
    print(f"YAML saved to {yaml_filename}")

def on_press(key):
    global current_key
    try:
        k = key.char
    except AttributeError:
        k = str(key)
    
    if key == keyboard.Key.space:
        print("Spacebar key pressed")
        key_log.append((k, time.time()))
        print(f"Key {k} pressed.")
        stop_event.set()  # Signal to stop recording
    if k == current_key:
        key_log.append((k, time.time()))
        print(f"Key {k} pressed.")
        stop_event.set()  # Signal to stop recording

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def start_recording(keyboard_name, keyboard_type, switch_color, keyboard_size, keyboard_layout, keyboard_sizes):
    global device_index, current_key, stop_event
    print(keyboard_layout)
    print(keyboard_dict)
    starting_idx = input("Select the index to start at.")
    resorted_dict = remove_keys_before_start_key(int(starting_idx))
    keys_to_press = list(resorted_dict.values())
    print("Press ESC to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        device_index = select_device()
        for key in keys_to_press:
            print(f"\nCurrent key to record is: {key}.")
            print(f"WAIT FOR THE COUNTDOWN BEFORE PRESSING ANYTHING!!!")
            created_yamls = []
            while len(created_yamls) < number_of_recordings:
                current_key = key
                start_event = threading.Event()
                stop_event = threading.Event()
                current_time = int(time.time())
                if current_key in forbidden_keys.keys():
                    filekey = forbidden_keys[current_key]
                    filename = f"data/key_data/key_press_{filekey}_{current_time}.wav"
                else:
                    filename = f"data/key_data/key_press_{current_key}_{current_time}.wav"
                recording_thread = threading.Thread(target=record_audio, args=(device_index, recording_duration, filename, start_event, stop_event))
                recording_thread.start()
                start_event.wait()  # Wait until recording has started
                recording_thread.join()
                for i in range(2, 0, -1):
                    print(f"Starting in {i}...")
                    time.sleep(1)
                    if i == 1:
                        recording_thread.join()
                print(f"Press {current_key} now!")
                if stop_event.is_set():
                    save_yaml(filename, current_key, current_time, keyboard_name, keyboard_type, switch_color, keyboard_size)
                    created_yamls.append(filename)
                else:
                    if os.path.exists(filename):
                        os.remove(filename)
                        if len(created_yamls) == 0:
                            continue
                    print(f"No key press detected. Reprompting for {current_key}.")
                if not listener.running:
                    break
            print(f"\n\nFinished recording {current_key} {number_of_recordings} times.")
            print(f"\n\nCheck the recording is audible and not static. (only the first time)")
            print(f"Press Enter to continue to the next key and wait for the prompt.")
            input()
    print("Key logging stopped.")
    with open('data/key_data/key_log.txt', 'w') as f:
        f.write(f"Keyboard Name: {keyboard_name}\n")
        f.write(f"Keyboard Type: {keyboard_type}\n")
        if keyboard_type.lower() == "mechanical":
            f.write(f"Switch Type: {switch_color}\n")
        f.write(f"Keyboard Size: {keyboard_size}\n")
        f.write("Key Logs:\n")
        for key, timestamp in key_log:
            f.write(f"{key}\t{timestamp}\n")
