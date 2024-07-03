import yaml

def read_keystrokes_as_string(filename):
    # Load the YAML file
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    
    # Get the list of keystrokes
    keystrokes = data.get('keystrokes', [])
    
    # Convert the list of keystrokes to a string
    result = ''
    for key in keystrokes:
        if key == 'Key.space':
            result += ' '
        else:
            result += key
    
    return result

# Example usage
keystrokes_str = read_keystrokes_as_string('data/sentence_data/keystrokes_1720009231.yaml')
print(keystrokes_str)