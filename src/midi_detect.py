"""
identify_and_select_midi_device function is responsible for identifying and selecting a MIDI input device. Here's a breakdown of what it does:

It initializes the Pygame MIDI module using pygame.midi.init().
It retrieves the number of available MIDI devices using pygame.midi.get_count().
If no MIDI devices are detected, it prints a message, quits the Pygame MIDI module, and returns None.
If MIDI devices are found, it prints the number of available MIDI input devices.
It iterates over the MIDI devices and prints information (ID and name) for each device that supports input.
It selects a specific MIDI device by its ID.
If the selected device number is invalid, it prints a message, quits the Pygame MIDI module, and returns None.
It creates and returns an input_device using pygame.midi.Input(device_number_select).

The receive_midi_input function receives MIDI input from a specified MIDI input device. Here's a breakdown of what it does:

It takes the midi_input_device as a parameter, which should be an instance of pygame.midi.Input.
It enters a continuous loop to receive MIDI input.
It checks if there are any MIDI messages available using midi_input_device.poll().
If there are MIDI messages, it reads up to 10 MIDI events using midi_input_device.read(10).
It processes each MIDI event by extracting the MIDI data components (status, note, velocity) from the event.
It yields a dictionary containing the extracted MIDI data for further processing.
The loop continues until the running flag is set to False.
"""

import pygame.midi

def identify_device():
    pygame.midi.init()  # Initialize the Pygame MIDI module

    device_count = pygame.midi.get_count()  # Get the number of available MIDI devices

    if device_count == 0:  # Check if no MIDI devices are detected
        print("No MIDI devices detected.")
        pygame.midi.quit()  # Quit Pygame MIDI module
        return None

    select_device(device_count)


def select_device(device_count):
    print(
        "Number of available MIDI input devices:", device_count
    )  # Print the number of available MIDI devices

    # Iterate over the MIDI devices and print information for each device
    for i in range(device_count):
        device_info = pygame.midi.get_device_info(i)
        device_name = device_info[1].decode(
            "utf-8"
        )  # Decode the device name from bytes to a string
        device_input = device_info[2]  # Check if the device supports input
        if device_input:
            print(
                f"Input ID: {i}, Name: {device_name}"
            )  # Print the ID and name of the MIDI input device

    device_num = 1  # Select a specific MIDI device by its ID (e.g., 1)

    if device_num >= device_count:  # Check if the selected device number is valid
        print("Invalid device number selected.")
        pygame.midi.quit()  # Quit Pygame MIDI module
        return None

    print("Selected Device Number is:", device_num)

    # Select the desired MIDI input device
    try:
        input_device = pygame.midi.Input(device_num)
        return input_device
    except pygame.midi.MidiException as e:
        print(str(e))
        pygame.midi.quit()
        return None


def receive_input(midi_input_device):
    # Main loop to receive MIDI input
    if pygame.midi.get_init() == False:
        raise RuntimeError("pygame.midi not initialised.")

    running = True
    while running:
        # Check if there are any MIDI messages available
        if midi_input_device.poll():
            # Read the MIDI messages
            midi_events = midi_input_device.read(10)  # Read up to 10 MIDI events

            # Process the MIDI messages
            for event in midi_events:
                # Extract MIDI data from the event
                data = event[
                    0
                ]  # The MIDI data is stored in the first element of the event tuple

                # Extract the specific MIDI components from the data
                status = data[
                    0
                ]  # The first byte of the MIDI data represents the status byte
                note = data[
                    1
                ]  # The second byte of the MIDI data represents the note value
                velocity = data[
                    2
                ]  # The third byte of the MIDI data represents the velocity or intensity of the MIDI event

                # Print the MIDI message debug line
                # print("Received MIDI message: Status={status}, Note={note}, Velocity={velocity}")

                # More Functionality can go here:
                yield {"status": status, "note": note, "velocity": velocity}


# How to Call the device detection function once and store it in a variable
# input_device = identify_and_select_midi_device()

# Main loop for MIDI input detection; DEBUG LINE
# while True:
# receive_input(input_device)
