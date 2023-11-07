import pygame.midi

def identify_device() -> pygame.midi.Input | None:
    """
    Initializes and identifies a MIDI input device using the Pygame MIDI module.

    This function serves as the entry point for setting up and identifying a MIDI input device.
    It performs the following steps:
    1. Initializes the Pygame MIDI module.
    2. Retrieves the number of available MIDI devices using pygame.midi.get_count().
    3. If no MIDI input devices are detected, it prints a message, quits the Pygame MIDI module, and returns None.
    4. If MIDI devices are found, it proceeds to the select_device function to choose and configure a specific device.

    Returns:
        pygame.midi.Input | None: An instance of the selected MIDI input device or None if no devices are available.
    """
    pygame.midi.init()
    device_count: int = pygame.midi.get_count()
    if device_count == 0:
        pygame.midi.quit()
        return None
    return select_device(device_count)

def select_device(device_count) -> pygame.midi.Input | None:
    """
    Selects a MIDI input device by its ID from the available options.

    This function prints information about the available MIDI input devices, including their IDs and names.
    It allows you to select a specific MIDI device by providing its ID. If the selected device number is invalid,
    it handles the error gracefully and returns None.

    Args:
        device_count (int): The number of available MIDI input devices.

    Returns:
        pygame.midi.Input | None: An instance of the selected MIDI input device or None if the selection is invalid.

    Note:
        Before using this function, ensure that you've initialized the Pygame MIDI module.
    """
    print(
        "Number of available MIDI input devices:", device_count
    )

    for i in range(device_count):
        device_info: tuple = pygame.midi.get_device_info(i)
        device_name: str = device_info[1].decode(
            "utf-8"
        )  # Decode the device name from bytes to a string
        device_input: int = device_info[2]  # Check if the device supports input
        if device_input:
            print(
                f"Input ID: {i}, Name: {device_name}"
            )

    device_num: int = 1  # Select a specific MIDI device by its ID (e.g., 1)

    if device_num >= device_count:  # Check if the selected device number is valid
        print("Invalid device number selected.")
        pygame.midi.quit()
        return None

    print("Selected Device Number is:", device_num)

    try:
        input_device: pygame.midi.Input = pygame.midi.Input(device_num)
        return input_device
    except pygame.midi.MidiException as e:
        print(str(e))
        pygame.midi.quit()
        return None

def receive_input(midi_input_device):
    """
    This function continuously receives and processes MIDI input from a specified MIDI input device.

    Args:
        midi_input_device (pygame.midi.Input): The MIDI input device to receive input from.

    Yields:
        dict: A dictionary containing the extracted MIDI data for each received MIDI event.
              Each dictionary includes the following keys:
              - 'status': The status byte of the MIDI event.
              - 'note': The note value associated with the MIDI event.
              - 'velocity': The velocity or intensity of the MIDI event.

    Raises:
        RuntimeError: If `pygame.midi` is not initialized, indicating that the MIDI subsystem
                      has not been properly set up.

    The function continuously listens for MIDI input from the specified `midi_input_device`.
    It extracts and processes MIDI messages as they arrive, yielding dictionaries
    containing the individual components of each MIDI event.

    The function is designed to be used in a loop, and it will keep running until
    stopped externally, making it suitable for real-time MIDI input processing.

    Note: Make sure to initialize the `pygame.midi` subsystem before calling this function.
    """
    if pygame.midi.get_init() == False:
        raise RuntimeError("pygame.midi not initialised.")

    running: bool = True
    while running:
        if midi_input_device.poll():
            midi_events = midi_input_device.read(10)  # Read up to 10 MIDI events
            for event in midi_events:
                data = event[0]  # The MIDI data is stored in the first element of the event tuple
                status = data[0]  # The first byte of the MIDI data represents the status byte
                note = data[1]  # The second byte of the MIDI data represents the note value
                velocity = data[2]  # The third byte of the MIDI data represents the velocity or intensity of the MIDI event
                yield {"status": status, "note": note, "velocity": velocity}