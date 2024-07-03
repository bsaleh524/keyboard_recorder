# keyboard_recorder
Data collection of keyboard and microhpone info per Adavanced Applied Machine Learning for JHU's research project(SUmmer 2024).

```python
\_______________________MICROPHONE_________________________/
|__________________________________________________________|
| --- |____________________________________________________|
|__________________________________________________________|
| ` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 | - | = |------|
|----------------------------------------------------------|
| ---| Q | W | E | R | T | Y | U | I | O | P | [ | ] |  \  |
|----------------------------------------------------------|
| ---- | A | S | D | F | G | H | J | K | L | ; | ' | ----- |
|----------------------------------------------------------|
| ----- | Z | X | C | V | B | N | M | , | . | / |   -----  |
|----------------------------------------------------------|
|---- | --- | --- |         Space         | --- | -- | ----|
|----------------------------------------------------------|
```

- `key_audio_recorder.py` records individual keystrokes. Pick a microphone and then it prompts for 10 regular presses of the keys.
- `sentence_audio_recorder.py` records sentences. Pick a microphone and then prompts for a sentence. After typing, hit escape to finish the recording. 

## Installation and setup
* This package isn't meant to be installed. Just run from the cloned down folder. To install dependencies, it requires python 3.9+.
* Create a virtual environment

`python3 -m venv keyboard_env`

* Then activate it

- Windows
`keyboard_env\Scripts\activate`

- Mac
`source keyboard_env/bin/activate`

* Then install the requirements.

`pip install -r requirements.txt`

To record keys, use `python key_audio_recorder.py`
To record a sentence, use `python sentence_audio_recorder.py`

## Privacy Concerns

The only data collected is the keyboard information you personally provide in the beginning(brand, switch color...), info of your chosen microphone selected as a recording device, the key pressed, and the audio of you typing the key. There is no additional data grabbed and no way data can be traced back to you.

Here is an output of information collected for each key press. You can find this in the `sample_data` folder.

```yaml
default_high_input_latency: 0.0421875
default_high_output_latency: 0.1
default_low_input_latency: 0.03285416666666666
default_low_output_latency: 0.01
default_samplerate: 48000.0
hostapi: 0
index: 0
key_pressed: /
keyboard_name: Macbook Pro 2021
keyboard_size: 65%_Compact(Default for Macbooks)
keyboard_type: scissor
max_input_channels: 1
max_output_channels: 0
name: MacBook Pro Microphone
switch_color: null
timestamp: 1720009201
```

And here for a sentence:

```yaml
keystrokes:
- w
- a
- d
- d
- u
- p
- Key.space
- d
- e
- m
- o
- n
- s
- ','
- Key.space
- i
- t
- s
- Key.space
- m
- e
- ','
- Key.space
- y
- a
- Key.space
- b
- o
- i
```
