# keyboard_recorder
Data collection of keyboard and microphone info per Adavanced Applied Machine Learning for JHU's research project(Summer 2024). This will collect general keyboard information in a yaml and audio files containing 25 key presses for each key shown in the keyboard below. 

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

## Installation and setup
This package isn't meant to be installed. Just run from the cloned/downloaded repository. To install dependencies, it requires python 3.9+.

1. Create a virtual environment
    - `python3 -m venv keyboard_env`

2. Then activate it
    - Windows (Command Prompt): `source keyboard_env\Scripts\activate`  (IS THIS RIGHT??)
    - Mac/Linux (Terminal): `source keyboard_env/bin/activate`

3. Install the requirements.
    - `pip install -r requirements.txt`

## Steps

1. Record your keyboard information from `first_keyboard_setup_info.py`. This file will have you select information i need for processing between different keyboards.
    * `python first_keyboard_setup_info.`

2. To record keys, use `second_key_audio_recorder.py`. This will ask for permission to select a microphone and then record your key presses. Ensure your microphone is facing the keyboard and is placed towards the top row. If the microphone is simply next to the keyboard, that's ok too.
    * `python second_ley_audio_recorder.py`
    * You will be asked to record each key press 25 times. If something messes up, you can restart the script and select the next key.

## Privacy Concerns

The only data collected is the keyboard information you personally provide in the beginning(brand, switch color...), the key pressed, the audio of you typing the key. There is no additional data grabbed and no way data can be traced back to you. I'm just a grad student looking to get an A. Or a B- at the minimum haha.

Here is an output of information collected for each key keyboard. You can find this in the `sample_data` folder.

```yaml
keyboard_material: aluminum
keyboard_name: MacbookProM1
keyboard_size: 65%_Compact(Default for Macbooks)
keyboard_type: scissor
switch_color: null
```

Link to original paper dataset: https://github.com/JBFH-Dev/Keystroke-Datasets/tree/main

multi-modal modeling: https://rosenfelder.ai/multi-input-neural-network-pytorch/