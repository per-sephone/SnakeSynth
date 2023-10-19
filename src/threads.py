"""
Worker Class
The Worker class is a helper class that is used to run the audio processing in a separate thread 
to avoid blocking the GUI.

MidiInputWorker Class
The MidiInputWorker class is a part of a synthesizer GUI application written in Python using the 
PySide6 library. 
This class is responsible for handling MIDI input messages and connecting them to the generation of 
tones in the synthesizer.

MidiWorker Class:
The MidiWorker class is responsible for managing the MIDI input functionality in a separate thread. 
It initializes the MIDI system using pygame.midi.init() and defines a signal named start_midi_thread. 
This class is designed to work with the MidiInputWorker class to receive and process MIDI messages
concurrently without blocking the main user interface.
"""

from PySide6.QtCore import QObject, QRunnable, Slot, Signal
import pygame
from midi_detect import receive_input

# Thread worker
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()  # QtCore.Slot
    def run(self):
        self.fn(self.args[0])


# Definition of MidiThread class that inherits QObject
class MidiWorker(QObject):
    pygame.midi.init()
    # Define the start_midi_thread signal
    signal = Signal()  # establishes a signal to manipulate

    def __init__(
        self, input_device
    ):  # construct that is used for instances of MIDITHREAD class
        super().__init__()
        pygame.midi.init()
        self.input_device = input_device

    def start(self):
        self.signal.emit()

class MidiInputWorker(QRunnable):
    def __init__(self, input_device, main_widget):
        super(MidiInputWorker, self).__init__()
        
        self.input_device = input_device
        self.main_widget = main_widget

    @Slot()
    def run(self):
        for msg in receive_input(self.input_device):
            if msg["status"] == 144: # This is the note on message
                note_value = msg["note"]
                if note_value >= 12 and note_value < 122: 
                    try:
                        note_name = self.main_widget.pitch_shifted_keys[note_value - 24]
                        print("MIDI KEY NOTE PLAYED:", note_name)
                        self.main_widget.button_pressed_handler(note_name)
                    except IndexError:
                        print("Note value is out of range. Ignoring MIDI message.")
                    
            elif msg["status"] == 128: # note off message
                self.main_widget.button_released_handler() 