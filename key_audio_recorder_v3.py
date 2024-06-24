import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading
import random

# Asks for name. Cant choose between mech or membrane yet.

# Global variables to keep track of state
recording = False
key_log = []
keys_to_press = ['a', 'b', 'c', 'd', 'e', 'f', 'g']  # List of keys to be prompted

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
    else:
        print(f"Wrong key pressed: {k}. Expected: {current_key}. Please try again.")
        stop_event.set()  # Signal to stop recording

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def get_user_input():
    global name, keyboard_name, keyboard_type, switch_color
    name = input("Enter your name: ")
    keyboard_name = input("Enter the name of the keyboard: ")
    keyboard_type = input("Enter the type of keyboard (membrane or mechanical): ")
    if keyboard_type.lower() == "mechanical":
        switch_color = input("Enter the Cherry MX switch color type: ")

def main():
    global device_index, current_key, stop_event
    get_user_input()
    device_index = select_device()

    print("Press ESC to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while True:
            current_key = prompt_next_key()
            start_event = threading.Event()
            stop_event = threading.Event()
            recording_thread = threading.Thread(target=record_audio, args=(device_index, recording_duration + 0.5, f"key_press_{current_key}_{int(time.time())}.wav", start_event, stop_event))
            recording_thread.start()
            start_event.wait()  # Wait until recording has started
            print(f"Press {current_key} now!")
            recording_thread.join()

            if not listener.running:
                break

    print("Key logging stopped.")

    # Save key log
    with open('key_log.txt', 'w') as f:
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
