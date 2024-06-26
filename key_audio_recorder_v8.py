import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading
import random
import yaml
import os

# Asked to fix issue where each key didnt have a timer on it.
# Also, fix issue where if a wrong key/not key pressed, it counts.
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
keyboard_dict = {
    0:'`',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'0',11:'-',12:'=',13:'Backsp',
    14:'Tab',15:'Q',16:'W',17:'E',18:'R',19:'T',20:'Y',21:'U',22:'I',23:'O',24:'P',25:'[',26:']',27:'\\',
    28:'Caps',29:'A',30:'S',31:'D',32:'F',33:'G',34:'H',35:'J',36:'K',37:'L',38:';',39:'\'',40:'Enter',
    41:'Shift',42:'Z',43:'X',44:'C',45:'V',46:'B',47:'N',48:'M',49:',',50:'.',51:'/',52:'Shift',
    53:'Ctrl',54:'Win',55:'Alt',56:'Space',57:'Alt',58:'Fn',59:'Ctrl',60:'Esc'
}
keys_to_press = list(keyboard_dict.values())

# Parameters for audio recording
sample_rate = 44100  # Sample rate in Hz
recording_duration = 1  # Duration to record after each key press in seconds
stop_event = threading.Event()
current_key = None
device_index = None
audio_buffer = []
name = ""
keyboard_name = ""
keyboard_type = ""
switch_color = ""

def list_devices():
    devices = sd.query_devices()
    return devices

def select_device():
    devices = list_devices()
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")
    device_index = int(input("Select the recording device index: "))
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
        start_event.set()  # Signal that recording has started
        stop_event.wait(duration)  # Wait for the stop signal or timeout
        stream.stop()

    myrecording = np.array(audio_buffer)

    # Check and handle invalid values
    if not np.isfinite(myrecording).all():
        myrecording = np.nan_to_num(myrecording)
        print("Warning: Invalid values encountered in recording. Converted to zero.")

    wav.write(filename, sample_rate, np.int16(myrecording * 32767))
    print(f"Audio saved to {filename}")

def save_yaml(filename, key_pressed):
    data = {
        'name': name,
        'keyboard_name': keyboard_name,
        'keyboard_type': keyboard_type,
        'switch_color': switch_color if keyboard_type.lower() == 'mechanical' else None,
        'key_pressed': key_pressed
    }
    yaml_filename = filename.replace('.wav', '.yaml')
    with open(yaml_filename, 'w') as yaml_file:
        yaml.dump(data, yaml_file)
    print(f"YAML saved to {yaml_filename}")

def prompt_next_key():
    next_key = random.choice(keys_to_press)
    print(f"Next key to press: {next_key}")
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    return next_key

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

def get_user_input():
    global name, keyboard_name, keyboard_type, switch_color
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
        switch_color = input("Enter the Cherry MX switch color type: ")
    else:
        print("Invalid choice. Defaulting to membrane.")
        keyboard_type = "membrane"

def main():
    global device_index, current_key, stop_event
    get_user_input()
    device_index = select_device()

    print("Press ESC to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        for key in keys_to_press:
            count = 0
            while count < 10:
                current_key = key
                start_event = threading.Event()
                stop_event = threading.Event()
                filename = f"data/key_press_{current_key}_{int(time.time())}.wav"
                recording_thread = threading.Thread(target=record_audio, args=(device_index, recording_duration + 0.5, filename, start_event, stop_event))
                recording_thread.start()
                start_event.wait()  # Wait until recording has started
                print(f"Press {current_key} now!")

                for i in range(3, 0, -1):
                    print(f"Recording in {i}...")
                    time.sleep(1)

                recording_thread.join()

                if stop_event.is_set():
                    save_yaml(filename, current_key)
                    count += 1
                    print(f"Recorded {current_key}: {count}/10")
                else:
                    # If no key press or incorrect key press, delete the created audio file
                    if os.path.exists(filename):
                        os.remove(filename)
                    print(f"Incorrect key or no key press detected. Reprompting for {current_key}.")

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
            f.write(f"Cherry MX Switch Color: {switch_color}\n")
        f.write("Key Logs:\n")
        for key, timestamp in key_log:
            f.write(f"{key}\t{timestamp}\n")

if __name__ == "__main__":
    main()
