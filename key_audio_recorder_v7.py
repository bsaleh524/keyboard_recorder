import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading
import random
import yaml
import os
from printout import keyboard_layout, instructions, switches

# Asked to record each key 10 times, then prompt user
# before moving to next key too. Based on dictionary below.
# Problems: 
#   Give them a visual prompt of what's going on
#   Timer is not functioning for any keys
#   If a key is not pressed/wrong key, it counts it anyway
#   Requires visual prompt every 10 or so keys to let them know
#   requires newline so they can clearly see what keys are needed.
#   Esc key must be counted + Press right arrow to stop program.
#   if a failure happened, have them jump back in.
#   

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Global variables to keep track of state
recording = False
key_log = []
keyboard_dict = { # make lowercase
    0: '`', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: '-', 12: '=',
    13: 'q', 14: 'w', 15: 'e', 16: 'r', 17: 't', 18: 'y', 19: 'u', 20: 'i', 21: 'o', 22: 'p', 23: '[', 24: ']', 25:'\\',
    26: 'a', 27: 's', 28: 'd', 29: 'f', 30: 'g', 31: 'h', 32: 'j', 33: 'k', 34: 'l', 35: ';', 36: '\'',
    37: 'z', 38: 'x', 39: 'c', 40: 'v', 41: 'b', 42: 'n', 43: 'm', 44: ',', 45: '.', 46: '/', 47: ' ',
}
forbidden_keys = {'\\': 'bcksl',
                  '\'': 'apost',
                  '/': 'fwdsl',
                  keyboard.Key.space: "_"}
keyboard_sizes = {0: '100%_FullSize',
                  1: '96%_Compact',
                  2: '80%_Tenkeyless',
                  3: '75%_Compact_Tenkeyless',
                  4: '65%_Compact',
                  5: '60%_Mini',
                  6: 'Unk'}
# keys_to_press = list(keyboard_dict.values())

# Parameters for audio recording
sample_rate = 44100  # Sample rate in Hz
recording_duration = 2  # Duration to record after each key press in seconds
number_of_recordings = 1
stop_event = threading.Event()
current_key = None
device_index = None
audio_buffer = []
name = ""
keyboard_name = ""
keyboard_type = ""
keyboard_size = ""
switch_type = ""
recording_device_info = {}

def reorder_keyboard_dict(start_key):
    # Convert the dictionary to a list of tuples (key, value)
    items = list(keyboard_dict.items())
    
    # Find the index of the start_key
    start_index = items.index((start_key, keyboard_dict[start_key]))
    
    # Reorder the list so that the start_key is at the beginning
    reordered_items = items[start_index:] + items[:start_index]
    
    # Convert the reordered list back to a dictionary
    reordered_dict = dict(reordered_items)
    return reordered_dict

def list_devices():
    devices = sd.query_devices()
    return devices

def select_device():
    global recording_device_info
    devices = list_devices()
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")
    device_index = int(input("Select the recording device index: "))
    recording_device_info = {micinfo:devices[device_index][micinfo] for micinfo in devices[device_index].keys()}
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

def save_yaml(filename, key_pressed, timestamp):
    data = {
        'name': name,
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

    if k == current_key:
        key_log.append((k, time.time()))
        print(f"Key {k} pressed.")
        stop_event.set()  # Signal to stop recording

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def display_sizes():
    print("\nSelect a keyboard size by entering the corresponding index number:")
    for index, keysize in keyboard_sizes.items():
        print(f"{index}: {keysize}")

def display_switches(switches):
    print("\nSelect a switch by entering the corresponding index number:")
    for index, switch in switches.items():
        print(f"{index}: {switch}")

def get_user_input():
    global name, keyboard_name, keyboard_type, switch_color, keyboard_size
    name = input("Enter your name: ")
    keyboard_name = input("Enter the name of the keyboard: ")
    print("Select the type of keyboard:")
    print("1: Membrane")
    print("2: Mechanical")
    keyboard_type_index = int(input("Enter the index of your choice: "))
    if keyboard_type_index == 1:
        keyboard_type = "membrane"
    elif keyboard_type_index == 2:
        keyboard_type = "mechanical"
        display_switches(switches)
        switch_color = switches[int(input("Enter the switch type index: "))]
    else:
        print("Invalid choice. Defaulting to membrane.")
        keyboard_type = "membrane"
    display_sizes()
    keyboard_size = input("Enter the switch type index: ")
    print("\n")
    print(keyboard_layout)
    print(instructions)
    input("Press the ENTER key when ready. You will select a recording device now.")

def main():
    global device_index, current_key, stop_event
    get_user_input()
    device_index = select_device()
    print(keyboard_layout)
    print(keyboard_dict)
    starting_idx = input("Select the index to start at.")
    resorted_dict = reorder_keyboard_dict(int(starting_idx))
    keys_to_press = list(resorted_dict.values())
    print("Press ESC to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        for key in keys_to_press:
            print(f"\nCurrent key to record is: {key}")
            created_yamls = []
            while len(created_yamls) < number_of_recordings:
                current_key = key
                start_event = threading.Event()
                stop_event = threading.Event()
                current_time = int(time.time())
                if current_key in forbidden_keys.keys():
                    filekey = forbidden_keys[current_key]
                    filename = f"data/key_press_{filekey}_{current_time}.wav"
                else:
                    filename = f"data/key_press_{current_key}_{current_time}.wav"
                recording_thread = threading.Thread(target=record_audio, args=(device_index, recording_duration, filename, start_event, stop_event))
                recording_thread.start()
                start_event.wait()  # Wait until recording has started
                recording_thread.join()
                for i in range(2, 0, -1):
                    print(f"Starting in {i}...")
                    time.sleep(1)
                    # if i == 2:
                        # recording_thread.start()
                        # start_event.wait()  # Wait until recording has started
                    if i == 1:
                        recording_thread.join()
                print(f"Press {current_key} now!")
                if stop_event.is_set():
                    save_yaml(filename, current_key, current_time)
                    created_yamls.append(filename)
                else:
                    # If no key press, delete the created audio file
                    if os.path.exists(filename):
                        os.remove(filename)
                        if len(created_yamls) == 0:
                            continue
                    print(f"No key press detected. Reprompting for {current_key}.")

                if not listener.running:
                    break

            print(f"Finished recording {current_key} 10 times. Press Enter to continue to the next key.")
            input()

    print("Key logging stopped.")

    # Save key log
    with open('data/key_log.txt', 'w') as f:
        f.write(f"Name: {name}\n")
        f.write(f"Keyboard Name: {keyboard_name}\n")
        f.write(f"Keyboard Type: {keyboard_type}\n")
        if keyboard_type.lower() == "mechanical":
            f.write(f"Switch Type: {switch_color}\n")
        f.write("Key Logs:\n")
        for key, timestamp in key_log:
            f.write(f"{key}\t{timestamp}\n")

if __name__ == "__main__":
    main()
