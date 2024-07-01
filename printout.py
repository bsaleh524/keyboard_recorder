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
    13: "Halo True"
}

keyboard_layout = """

\_______________________MICROPHONE_________________________/
|__________________________________________________________|
| Esc |____________________________________________________|
|__________________________________________________________|
| ` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 | - | = |Backsp|
|----------------------------------------------------------|
| Tab| Q | W | E | R | T | Y | U | I | O | P | [ | ] |  \  |
|----------------------------------------------------------|
| Caps | A | S | D | F | G | H | J | K | L | ; | ' | Enter |
|----------------------------------------------------------|
| Shift | Z | X | C | V | B | N | M | , | . | / |   Shift  |
|----------------------------------------------------------|
|---- | --- | --- |         Space         | --- | -- | ----|
|----------------------------------------------------------|
"""

keyboard_layout_index_map = """
| 54 |__________________________________________________________________|
|_______________________________________________________________________|
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 ||||||||   13    |
|-----------------------------------------------------------------------|
| 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 |  27  |
|-----------------------------------------------------------------------|
| 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 |        40 |
|-----------------------------------------------------------------------|
| 41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 | 49 | 50 | 51 ||            52 |
|-----------------------------------------------------------------------|
|---- | --- | --- |                 53                 | --- | -- | ----|
|-----------------------------------------------------------------------|
"""

keyboard_dict = {
    0:'`',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'0',11:'-',12:'=',13:'Backsp',
    14:'Tab',15:'Q',16:'W',17:'E',18:'R',19:'T',20:'Y',21:'U',22:'I',23:'O',24:'P',25:'[',26:']',27:'\\',
    28:'Caps',29:'A',30:'S',31:'D',32:'F',33:'G',34:'H',35:'J',36:'K',37:'L',38:';',39:'\'',40:'Enter',
    41:'Shift',42:'Z',43:'X',44:'C',45:'V',46:'B',47:'N',48:'M',49:',',50:'.',51:'/',52:'Shift',
    53:'Ctrl',54:'Win',55:'Alt',56:'Space',57:'Alt',58:'Fn',59:'Ctrl',60:'Esc'
}

instructions = """

####################### INSTRUCTIONS ############################
Thank you for helping out! Here's how it works.\n
The keyboard posted above shows all of the keys you will press.
You will be prompted to press the corresponding key per a prompt here.
Each key will be pressed 10 times. Each time, you will see a timer before a 
        'Press <KEY> now!' prompt appears. 
When it appears, press the key. You'll have 2 seconds to do it.\n
For example, when the 'a' key is prompted:\n
* 'Press a now!'
* You press the 'a' key
* Timer goes from 3...2...1
* 'Press a now!'
* You press the 'a' key
* Repeat until 10 samples are collected.\n

Repeat until all key presses and audio is recorded.\n
You'll start the next key on your own by
pressing LeftArrow to move on to the next letter.

If you got interrupted and want to start again, select what key to 
begin from after this prompt.

************************** SETUP *********************************
      
* Place the microphone you have at the top of your keyboard
* Record in an area with no noise
* Don't make a noise other than your keyboard(breath, sneeze, etc)
* Tap the key at the same level you would usually type.
* Fill in the other prompts as best as you can. The more accurate
      or descriptive your keyboard/switch names are, the better!

When you finish, zip up the data folder and send it to me:
                    bsaleh2@jh.edu  

"""



