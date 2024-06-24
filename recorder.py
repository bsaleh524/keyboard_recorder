import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading
import random

# Global variables to keep track of state
recording = False
key_log = []
keys_to_press = ['a', 'b', 'c', 'd', 'e', 'f', 'g']  # List of keys to be prompted

# Parameters for audio recording
sample_rate = 44100  # Sample rate in Hz
recording_duration = 1  # Duration to record after each key press in seconds

def list_devices():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")

def select_device():
    list_devices()
    device_index = int(input("Select the recording device index: "))
    return device_index

def record_audio(device, duration, filename):
    print(f"Recording audio for {duration} seconds on device {device}.")
    myrecording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, device=device)
    sd.wait()  # Wait until recording is finished
    wav.write(filename, sample_rate, np.int16(myrecording * 32767))
    print(f"Audio saved to {filename}")

def prompt_next_key():
    next_key = random.choice(keys_to_press)
    print(f"Next key to press: {next_key}")
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    print(f"Press {next_key} now!")
    return next_key

def on_press(key):
    global recording, key_log, current_key
    try:
        k = key.char
    except AttributeError:
        k = str(key)

    if k == current_key:
        key_log.append((k, time.time()))
        print(f"Key {k} pressed.")

        if not recording:
            recording = True
            threading.Thread(target=record_audio, args=(device_index, recording_duration, f"key_press_{k}_{int(time.time())}.wav")).start()
            recording = False

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def main():
    global device_index, current_key
    device_index = select_device()

    print("Press ESC to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while True:
            current_key = prompt_next_key()
            time.sleep(recording_duration + 1)  # Wait for the duration of the recording plus a small buffer

            if listener.running == False:
                break

    print("Key logging stopped.")

    # Save key log
    with open('key_log.txt', 'w') as f:
        for key, timestamp in key_log:
            f.write(f"{key}\t{timestamp}\n")

if __name__ == "__main__":
    main()
