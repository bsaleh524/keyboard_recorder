switches = {
    0: "Cherry MX Red",
    1: "Cherry MX Silent Red",
    2: "Cherry MX Black",
    3: "Cherry MX Silent Black",
    4: "Cherry MX Speed Silver",
    5: "Cherry MX Brown",
    6: "Cherry MX Clear",
    7: "Cherry MX Blue",
    8: "Cherry MX Green",
    9: "Cherry MX White",
    10: "Cherry MX Grey",
    11: "Cherry MX Nature White",
    12: "Halo Clear",
    13: "Halo True",
    14: "Unk/Not here(Clicky)",
    15: "Unk/Not here(Smooth)",
}

keyboard_layout = """

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
"""

keyboard_layout_index_map = """
| -- |__________________________________________________________________|
|_______________________________________________________________________|
|  0 |  1 |  2 |  3 |  4 |  5 |  6 |  7 |  8 |  9 | 10 | 11 | 12 ||||||||   --    |
|-----------------------------------------------------------------------|
| -- | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 |  25  |
|-----------------------------------------------------------------------|
| --- | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 |       -- |
|-----------------------------------------------------------------------|
| --    | 37 | 38 | 39 | 40 | 41 | 42 | 43 | 44 | 45 | 46 |          -- |
|-----------------------------------------------------------------------|
|---- | --- | --- |                 47                 | --- | -- | ----|
|-----------------------------------------------------------------------|
"""


key_instructions = """

************************** Instructions *********************************
      
1. Place the microphone you have at the top of your keyboard(by numbers)
2. Record in an area with no noise.
3. Don't make a noise other than your keyboard(breath, sneeze, etc).
4. Tap the key at the same level you would usually type.
5. Your OS may prompt for audio permissions. Allow, and restart script(first time only).

* This takes maybe 15-20 minutes to do.
* If you mess up, you can go back to the key you messed up on and continue by restarting
    the script.
* You will be given windows to move to the next key. You can pause before moving
    to the next key.
* When you start a new key, there will be a blank before it says it's saving. I can't
    get around that bug but just know after that, the real recordings will start.
* When the current key has enough recordings, it will ask to press 'Enter' to go
    to the next key. When you see that, you don't have to press the same key again.

When you finish, zip up the data folder and let me know in discord.
You'll get a link to upload it.

***PLEASE LISTEN TO A RECORDED FILE TO CONFIRM YOU SELECTED THE CORRECT DEVICE!**

"""


sent_instructions = """

************************** Instructions *********************************
      
When you you ready, hit enter to start typing. You can only use the
keys indicated above from the diagram. Sentences are expected to be lowercase.

Example: "whatup demons, its me, ya boi."

***PLEASE LISTEN TO A RECORDED FILE TO CONFIRM YOU SELECTED THE CORRECT DEVICE!**

When you finish, zip up the data folder and let me know in discord.
You'll get a link to upload it.
"""
