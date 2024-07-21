import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import time
import threading
import os
from datetime import datetime

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
recording_duration = 1.5  # Duration to record after each key press in seconds
number_of_recordings = 25
current_key = None
device_index = None
audio_buffer = []
recording_device_info = {}

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

def record_audio(device, duration, start_event, stop_event):
    global audio_buffer
    audio_buffer = []

    stream = sd.InputStream(samplerate=sample_rate, channels=1, device=device, callback=audio_callback)
    with stream:
        stream.start()
        start_event.set()  # Signal that recording has started
        stop_event.wait(duration)  # Wait for the stop signal or timeout
        stream.stop()

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

def main():
    global device_index, current_key, stop_event
    device_index = select_device()
    keys_to_press = list(keyboard_dict.values())
    print("Press ESC to stop.")
    print("\nYou will be prompted to press each key 25 times. Wait for the countdown before pressing anything.")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        for key in keys_to_press:
            print(f"\nCurrent key to record is: {key}.")
            print(f"Press ENTER to start recording for this key.")
            input()
            created_yamls = []
            combined_recording = []

            while len(created_yamls) < number_of_recordings:
                current_key = key
                start_event = threading.Event()
                stop_event = threading.Event()
                recording_thread = threading.Thread(target=record_audio, args=(device_index, recording_duration, start_event, stop_event))
                recording_thread.start()
                start_event.wait()  # Wait until recording has started
                for i in range(2, 0, -1):
                    print(f"Starting in {i}...")
                    time.sleep(1)
                print(f"Press {current_key} now!")
                stop_event.wait()  # Wait until the key is pressed or timeout
                recording_thread.join()

                combined_recording.extend(audio_buffer)

                if stop_event.is_set():
                    created_yamls.append(current_key)
                else:
                    print(f"No key press detected. Reprompting for {current_key}.")

                if not listener.running:
                    break

            # Save combined recording
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            if current_key in forbidden_keys.keys():
                filekey = forbidden_keys[current_key]
                filename = f"data/key_data/key_press_{filekey}_{current_time}.wav"
            else:
                filename = f"data/key_data/key_press_{current_key}_{current_time}.wav"

            combined_recording = np.array(combined_recording)
            wav.write(filename, sample_rate, np.int16(combined_recording * 32767))
            print(f"Combined audio saved to {filename}")

            print(f"\n\nFinished recording {current_key} {number_of_recordings} times.")
            print(f"\n\nCheck the recording is audible and not static.(only the first time)")
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
