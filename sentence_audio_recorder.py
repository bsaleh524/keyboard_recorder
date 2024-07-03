import threading
import time
import sounddevice as sd
import numpy as np
import wave
import yaml
from pynput import keyboard
import os
import scipy.io.wavfile as wav

# Define global variables
recording = False
keystrokes = []
audio_buffer = []
sample_rate = 44100  # Sample rate for audio recording

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
            time.sleep(1)
            stream.stop()

        myrecording = np.array(audio_buffer)

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
    global recording, keystrokes

    if key == keyboard.Key.esc:
        recording = False
        return False  # Stop listener
    else:
        try:
            keystrokes.append(key.char)
        except AttributeError:
            keystrokes.append(str(key))

# Function to save audio data to a .wav file
def save_audio(filename):
    global audio_buffer, sample_rate

    audio_data_np = np.concatenate(audio_buffer, axis=0)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data_np.tobytes())

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
    global recording

    device_index = select_device()

    print('Waiting for recording thread to start')
    
    recording = True
    start_event = threading.Event()
    stop_event = threading.Event()
    current_time = int(time.time())
    filename = f"sentence_data/sentence_{current_time}.wav"
    audio_thread = threading.Thread(target=record_audio, args=(device_index, 30, filename, start_event, stop_event))
    audio_thread.start()
    # start_event.wait() # Wait for recording to start

    print("Please start typing. Press ESC to stop recording.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    stop_event.set()
    audio_thread.join()

    folder_path = "recordings"
    ensure_folder_exists(folder_path)
    audio_filename = os.path.join(folder_path, f"{filename}")
    yaml_filename = os.path.join(folder_path, f"keystrokes_{current_time}.yaml")

    # os.rename("temp.wav", audio_filename)
    save_keystrokes(yaml_filename)

    print(f"Audio saved to {audio_filename}")
    print(f"Keystrokes saved to {yaml_filename}")

if __name__ == "__main__":
    main()
