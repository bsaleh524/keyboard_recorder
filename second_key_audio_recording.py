import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading
import os
from datetime import datetime
from printout import keyboard_layout

# Ensure the data directory exists
if not os.path.exists('data/key_data'):
    os.makedirs('data/key_data')

# Global variables to keep track of state
recording = False
key_log = []
keyboard_dict = { 
    0: '`', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: '-', 12: '=',
    13: 'q', 14: 'w', 15: 'e', 16: 'r', 17: 't', 18: 'y', 19: 'u', 20: 'i', 21: 'o', 22: 'p', 23: '[', 24: ']', 25:'\\',
    26: 'a', 27: 's', 28: 'd', 29: 'f', 30: 'g', 31: 'h', 32: 'j', 33: 'k', 34: 'l', 35: ';', 36: '\'',
    37: 'z', 38: 'x', 39: 'c', 40: 'v', 41: 'b', 42: 'n', 43: 'm', 44: ',', 45: '.', 46: '/', 47: keyboard.Key.space,
}
forbidden_keys = {'\\': 'bcksl', '\'': 'apost', '/': 'fwdsl', keyboard.Key.space: "space"}

# Parameters for audio recording
sample_rate = 44100  # Sample rate in Hz
current_key = None
device_index = None
audio_buffer = []
recording_device_info = {}
desired_key_count = 25

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

def remove_keys_before_start_key(start_key):
    # Convert the dictionary to a list of tuples (key, value)
    items = list(keyboard_dict.items())

    # Find the index of the start_key
    start_index = items.index((start_key, keyboard_dict[start_key]))

    if start_index is None:
        raise ValueError(f"Key '{start_key}' not found in dictionary")

    # Remove all items before the start_index
    remaining_items = items[start_index:]

    # Convert the remaining items back to a dictionary
    remaining_dict = dict(remaining_items)
    return remaining_dict

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_buffer.extend(indata.copy())

def record_audio(device, start_event, stop_event):
    global audio_buffer
    audio_buffer = []

    stream = sd.InputStream(samplerate=sample_rate, channels=1, device=device, callback=audio_callback)
    with stream:
        stream.start()
        start_event.set()  # Signal that recording has started
        stop_event.wait()  # Wait for the stop signal
        stream.stop()

def on_press(key):
    global current_key, press_count
    try:
        k = key.char
    except AttributeError:
        k = str(key)

    if key == keyboard.Key.space:
        print("Spacebar key pressed")
        key_log.append((k, time.time()))
        press_count += 1
        print(f"Key {k} pressed.")
        if press_count >= desired_key_count:
            stop_event.set()  # Signal to stop recording
    
    if k == current_key:
        key_log.append((k, time.time()))
        press_count += 1
        print(f"Key {k} pressed. Count: {press_count}")
        if press_count >= desired_key_count:
            stop_event.set()  # Signal to stop recording

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def main():
    global device_index, current_key, stop_event, press_count
    device_index = select_device()
    print(keyboard_layout)
    print(keyboard_dict)
    starting_idx = input("Select the index to start at.")
    resorted_dict = remove_keys_before_start_key(int(starting_idx)) # reorder_keyboard_dict(int(starting_idx))
    keys_to_press = list(resorted_dict.values())
    print("Press ESC to stop.")
    print(f"\nYou will be prompted to press each key {desired_key_count} times after a countdown completes.")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        for key in keys_to_press:
            print(f"\nCurrent key to record is: {key}.")
            print(f"Press ENTER to start recording for this key.")
            input()
            time.sleep(0.5)
            press_count = 0
            current_key = key
            start_event = threading.Event()
            stop_event = threading.Event()
            recording_thread = threading.Thread(target=record_audio, args=(device_index, start_event, stop_event))
            recording_thread.start()
            for i in range(3, 0, -1):
                print(f"Starting in {i}...")
                time.sleep(1)
            start_event.wait()  # Wait until recording has started
            print(f"Press {current_key} now {desired_key_count} times!")

            recording_thread.join()

            # Save the recording
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            if current_key in forbidden_keys.keys():
                filekey = forbidden_keys[current_key]
                filename = f"data/key_data/key_press_{filekey}_{current_time}.wav"
            else:
                filename = f"data/key_data/key_press_{current_key}_{current_time}.wav"

            combined_recording = np.array(audio_buffer)
            wav.write(filename, sample_rate, np.int16(combined_recording * 32767))
            print(f"Audio saved to {filename}")

            print(f"\n\nFinished recording {current_key} {desired_key_count} times.")
            print(f"\n\nCheck the recording is audible and not static (only the first time).")
            print(f"Press Enter to continue to the next key and wait for the prompt.")
            input()

    print("Key logging stopped.")

    # Save key log
    with open('data/key_data/key_log.txt', 'w') as f:
        f.write("Key Logs:\n")
        for key, timestamp in key_log:
            f.write(f"{key}\t{timestamp}\n")

if __name__ == "__main__":
    main()