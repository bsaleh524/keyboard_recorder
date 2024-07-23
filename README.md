# keyboard_recorder
Data collection of keyboard and microphone info per Adavanced Applied Machine Learning for JHU's research project(Summer 2024).

Link to original paper dataset: https://github.com/JBFH-Dev/Keystroke-Datasets/tree/main

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

## Steps

1. Record your keyboard information from `python first_keyboard_setup_info.py`
2. To record keys, use `python second_key_audio_recorder.py`

## Privacy Concerns

The only data collected is the keyboard information you personally provide in the beginning(brand, switch color...), info of your chosen microphone selected as a recording device, the key pressed, and the audio of you typing the key. There is no additional data grabbed and no way data can be traced back to you.

Here is an output of information collected for each key press. You can find this in the `sample_data` folder.

```yaml
keyboard_name: Macbook Pro 2021
keyboard_size: 65%_Compact(Default for Macbooks)
keyboard_type: scissor
name: MacBook Pro Microphone
```