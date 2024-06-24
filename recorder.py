import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading

# Global variables to keep track of state
recording = False
key_log = []

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

def on_press(key):
    global recording, key_log
    try:
        k = key.char
    except AttributeError:
        k = str(key)

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
    global device_index
    device_index = select_device()
    print("Press ESC to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    print("Key logging stopped.")

    # Save key log
    with open('key_log.txt', 'w') as f:
        for key, timestamp in key_log:
            f.write(f"{key}\t{timestamp}\n")

if __name__ == "__main__":
    main()
