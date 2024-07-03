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

##
Privacy

