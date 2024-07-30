import os
import yaml
from printout import keyboard_layout, key_instructions, switches

def display_switches(switches):
    print("\nSelect a switch by entering the corresponding index number:")
    for index, switch in switches.items():
        print(f"{index}: {switch}")

def display_sizes(keyboard_sizes):
    print("\nSelect a keyboard size by entering the corresponding index number:")
    for index, keysize in keyboard_sizes.items():
        print(f"{index}: {keysize}")

def get_user_input(keyboard_layout, key_instructions, switches, keyboard_sizes):
    keyboard_name = input("Enter the name of the keyboard: ")
    print("Select the type of keyboard:")
    print("1: Membrane")
    print("2: Mechanical")
    print("3: Magic Keyboard(Scissor) for Macs")
    keyboard_type_index = int(input("Enter the index of your choice: "))
    if keyboard_type_index == 1:
        keyboard_type = "membrane"
        switch_color = None
    elif keyboard_type_index == 2:
        keyboard_type = "mechanical"
        display_switches(switches)
        switch_color = switches[int(input("Enter the switch type index: "))]
    elif keyboard_type_index == 3:
        keyboard_type = "scissor"
        switch_color = None
    else:
        print("Invalid choice. Defaulting to membrane.")
        keyboard_type = "membrane"
        switch_color = None
    display_sizes(keyboard_sizes)
    keyboard_size = keyboard_sizes[int(input("Enter the keyboard size index: "))]
    keyboard_material = input("Enter the material of your keyboard(Wood, plastic, aluminum,etc): ")
    return keyboard_name, keyboard_type, switch_color, keyboard_size, keyboard_material

def save_to_yaml(filename, keyboard_name, keyboard_type, switch_color, keyboard_size, keyboard_material):
    data = {
        'keyboard_name': keyboard_name,
        'keyboard_type': keyboard_type,
        'keyboard_size': keyboard_size,
        'keyboard_material': keyboard_material,
        'switch_color': switch_color if keyboard_type.lower() == 'mechanical' else None
    }
    with open(filename, 'w') as yaml_file:
        yaml.dump(data, yaml_file)
    print(f"Configuration saved to {filename}")

def main():
    # Ensure the data directory exists
    if not os.path.exists('data/key_data'):
        os.makedirs('data/key_data')
    keyboard_sizes = {
        6: 'Unk',
        5: '100%_FullSize',
        4: '96%_Compact',
        3: '80%_Tenkeyless',
        2: '75%_Compact_Tenkeyless',
        1: '65%_Compact(Default for Macbooks)',
        0: '60%_Mini',
    }
    
    keyboard_name, keyboard_type, switch_color, keyboard_size, keyboard_material = get_user_input(keyboard_layout, key_instructions, switches, keyboard_sizes)
    config_filename = f"data/key_data/{keyboard_name}_config.yaml"
    save_to_yaml(config_filename, keyboard_name, keyboard_type, switch_color, keyboard_size, keyboard_material)
    print("Configuration saved. Exiting setup.")

if __name__ == "__main__":
    main()
