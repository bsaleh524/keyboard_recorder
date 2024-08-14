# keyboard_recorder
Data collection of keyboard keystrokes for JHU Project. This will collect general keyboard information in a yaml and audio files containing 25 key presses for each key shown in the keyboard below. 

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

## Recording
### Installation and setup
This package isn't meant to be installed. Just run from the cloned/downloaded repository. To install dependencies, it requires python 3.9+.

1. Create a virtual environment
    - `python3 -m venv keyboard_env`

2. Then activate it
    - Windows (Command Prompt): `keyboard_env\Scripts\activate`
    - Mac/Linux (Terminal): `source keyboard_env/bin/activate`

3. Install the requirements.
    - `pip install -r requirements.txt`

### Actual recording
1. Record your keyboard information from `first_keyboard_setup_info.py`. This file will have you select information i need for processing between different keyboards.
    * `python first_keyboard_setup_info.py`

2. To record keys, use `second_key_audio_recorder.py`. This will ask for permission to select a microphone and then record your key presses. Ensure your microphone is facing the keyboard and is placed towards the top row. If the microphone is simply next to the keyboard, that's ok too.
    * `python second_ley_audio_recorder.py`
    * You will be asked to record each key press 25 times. If something messes up, you can restart the script and select the next key.

All data you personally record should go in the `data/new_data` folder to be included in preprocessing and training scripts.

## Training and testing CoAtNet Fusion Model

Simply run the `preprocessing/preprocess_and_train.ipynb` notebook to run all five experiments. It will automatically preprocess the data and train on all five experiments.

## Running the Tableau Dashboard

The dashboard is already live at [this link](https://public.tableau.com/app/profile/basem.saleh/viz/KeyboardDashboard/Dashboard1) using data from the `data/link.txt` folder. The Tableau dashboard file is included in the Tableau folder for your editing usage. The `preprocess_for_dataviz.ipynb` will preprocess the data required to create the tableau dashboard into two files: `individual_keys.csv` and `keyboard_map_final_df_5.csv`. Both of these are required to create the dashboard. TO run the current dashboard, load in both csvs within this current repository.

## Privacy Concerns

The only data collected is the keyboard information you personally provide in the beginning(brand, switch color...), the key pressed, the audio of you typing the key. There is no additional data grabbed and no way data can be traced back to you.

Here is an output of information collected for each key keyboard. You can find this in the `sample_data` folder.

```yaml
keyboard_material: aluminum
keyboard_name: MacbookProM1
keyboard_size: 65%_Compact(Default for Macbooks)
keyboard_type: scissor
switch_color: null
```

Link to original paper dataset: https://github.com/JBFH-Dev/Keystroke-Datasets/tree/main

fusion modeling: https://rosenfelder.ai/multi-input-neural-network-pytorch/