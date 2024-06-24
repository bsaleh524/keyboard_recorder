import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading
import random
import tkinter as tk
from tkinter import ttk, messagebox

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

def list_devices():
    devices = sd.query_devices()
    return devices

def select_device():
    devices = list_devices()
    device_names = [device['name'] for device in devices]
    return device_names

def record_audio(device, duration, filename, start_event, stop_event):
    print(f"Recording audio for {duration} seconds on device {device}.")
    myrecording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, device=device)
    start_event.set()  # Signal that recording has started
    stop_event.wait()  # Wait for the stop signal
    sd.stop()
    wav.write(filename, sample_rate, np.int16(myrecording * 32767))
    print(f"Audio saved to {filename}")

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

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Key Press Recorder")
        self.create_widgets()
        self.listener = None

    def create_widgets(self):
        self.device_label = ttk.Label(self.root, text="Select Recording Device:")
        self.device_label.pack(pady=5)

        self.devices = select_device()
        self.device_var = tk.StringVar(value=self.devices[0])
        self.device_menu = ttk.Combobox(self.root, textvariable=self.device_var, values=self.devices, state="readonly")
        self.device_menu.pack(pady=5)

        self.start_button = ttk.Button(self.root, text="Start", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.prompt_label = ttk.Label(self.root, text="", font=("Helvetica", 18))
        self.prompt_label.pack(pady=20)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_recording(self):
        global device_index, current_key, stop_event
        device_index = self.devices.index(self.device_var.get())
        self.start_button.config(state="disabled")

        def recording_thread():
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                self.listener = listener
                while True:
                    current_key = self.prompt_next_key()
                    start_event = threading.Event()
                    stop_event = threading.Event()
                    threading.Thread(target=record_audio, args=(device_index, recording_duration + 0.5, f"key_press_{current_key}_{int(time.time())}.wav", start_event, stop_event)).start()
                    start_event.wait()  # Wait until recording has started
                    self.prompt_label.config(text=f"Press {current_key} now!")
                    stop_event.wait()  # Wait for the stop signal

                    if not listener.running:
                        break

            self.start_button.config(state="normal")
            self.prompt_label.config(text="")

        threading.Thread(target=recording_thread).start()

    def prompt_next_key(self):
        next_key = random.choice(keys_to_press)
        self.prompt_label.config(text=f"Next key to press: {next_key}")
        for i in range(3, 0, -1):
            self.prompt_label.config(text=f"Starting in {i}...")
            time.sleep(1)
        return next_key

    def on_closing(self):
        if self.listener:
            self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

    # Save key log
    with open('key_log.txt', 'w') as f:
        for key, timestamp in key_log:
            f.write(f"{key}\t{timestamp}\n")
