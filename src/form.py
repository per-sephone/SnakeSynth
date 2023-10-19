"""
Overview
This code represents a synthesizer GUI application written in Python using the PySide6 library.
The synthesizer UI  supports multiple waveforms including sine, square, sawtooth, and triangle waves
 with adjustable parameters attack, decay, sustain, and release (ADSR envelope), volume, pitch, and tone. 

Wave Generation
After defining the constants, the code generates waveforms for each key using different oscillators 
(sine, square, sawtooth, and triangle). These waveforms are stored in dictionaries for easy access.

Worker Class
The Worker class is a helper class that is used to run the audio processing in a separate thread 
to avoid blocking the GUI.

MainWidget Class
The MainWidget class represents the main widget of the synthesizer application. It inherits from 
the QWidget class provided by the PySide6 library. The class contains methods for handling UI events, 
such as button presses, knob changes, and waveform selection.

MidiInputWorker Class
The MidiInputWorker class is a part of a synthesizer GUI application written in Python using the 
PySide6 library. 
This class is responsible for handling MIDI input messages and connecting them to the generation of 
tones in the synthesizer.

MidiThread Class:
The MidiThread class is responsible for managing the MIDI input functionality in a separate thread. 
It initializes the MIDI system using pygame.midi.init() and defines a signal named start_midi_thread. 
This class is designed to work with the MidiInputWorker class to receive and process MIDI messages
concurrently without blocking the main user interface.
"""

import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QPushButton,
    QRadioButton,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import QFile, Qt, QObject, QRunnable, Slot, QThreadPool, Signal
from PySide6.QtUiTools import QUiLoader
from oscillator import (
    SineOscillator as sine,
    SquareOscillator as square,
    TriangleOscillator as triangle,
    SawtoothOscillator as saw,
)
from adsr import ADSREnvelope, State
from notefreq import NOTE_FREQS
from volume import Volume
from midi_detect import identify_and_select_midi_device
from midi_detect import receive_midi_input
import pygame
import sounddevice as sd
import numpy as np

sd.default.latency = "low"

SAMPLE_RATE = 48000
MAX_AMPLITUDE = 8192
DURATION = 0.2
DEFAULT_VOLUME = 9
DEFAULT_VOLUME_OFFSET = 9
DEFAULT_ATTACK = 2
DEFAULT_DECAY = 7
DEFAULT_SUSTAIN = 8
DEFAULT_RELEASE = 3
DEFAULT_PITCH = 3

# generate a oscillator for each key inside a dictionary
# {"A4" : SineOscillator
# ...
# }
# Note: due to saw wave and square wave implementation, generating them takes a lot longer, might need rework in the future.
sine_waves = {}
square_waves = {}
saw_waves = {}
triangle_waves = {}

for key in NOTE_FREQS:
    sine_waves[key] = sine(
        NOTE_FREQS[key], SAMPLE_RATE, MAX_AMPLITUDE, DURATION
    ).generate_wave()
    square_waves[key] = square(
        NOTE_FREQS[key], SAMPLE_RATE, MAX_AMPLITUDE, DURATION
    ).generate_wave()
    saw_waves[key] = saw(
        NOTE_FREQS[key], SAMPLE_RATE, MAX_AMPLITUDE, DURATION
    ).generate_wave()
    triangle_waves[key] = triangle(
        NOTE_FREQS[key], SAMPLE_RATE, MAX_AMPLITUDE, DURATION
    ).generate_wave()

# Key names in the GUI
GUI_KEY_NAMES = [
    "C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0",
    "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
    "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
    "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
    "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
    "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
    "C6", "C36", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", "A6", "A#6", "B6",
    "C7", "C#7", "D7" ,"D#7", "E7", "F7", "F#7", "G7", "G#7", "A7", "A#7", "B7"
]


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
class MidiThread(QObject):
    pygame.midi.init()
    # Define the start_midi_thread signal
    start_midi_thread = Signal()  # establishes a signal to manipulate

    def __init__(
        self, input_device
    ):  # construct that is used for instances of MIDITHREAD class
        super().__init__()
        pygame.midi.init()
        self.input_device = input_device

    def start(self):
        self.start_midi_thread.emit()

class MidiInputWorker(QRunnable):
    def __init__(self, input_device, main_widget):
        super(MidiInputWorker, self).__init__()
        
        self.input_device = input_device
        self.main_widget = main_widget

    @Slot()
    def run(self):
        for midi_message in receive_midi_input(self.input_device):
            # print("Yo! MIDI message:", midi_message) # debag line
            
            if midi_message["status"] == 144: # This is the note on message
                note_value = midi_message["note"]
                if note_value >= 12 and note_value < 122: 
                    try:
                        note_name = self.main_widget.pitch_shifted_keys[note_value - 24]
                        print("MIDI KEY NOTE PLAYED:", note_name)
                        self.main_widget.button_pressed_handler(note_name)
                    except IndexError:
                        print("Note value is out of range. Ignoring MIDI message.")
                    
            elif midi_message["status"] == 128: # note off message
                self.main_widget.button_released_handler() 


class MainWidget(
    QWidget
):  ### defines a class named MainWidget that inherits from QWidget class. The __init__() method initializes the object of the MainWidget class. The super() function is used to call the constructor of the parent class (QWidget) and to get the instance of the MainWidget class. This allows MainWidget to inherit all the attributes and methods from QWidget.
    def __init__(self):
        super(MainWidget, self).__init__()
        self.vol_ctrl = Volume(DEFAULT_VOLUME, DEFAULT_VOLUME_OFFSET)
        self.adsr_envelope = ADSREnvelope(DEFAULT_ATTACK, DEFAULT_DECAY, DEFAULT_SUSTAIN, DEFAULT_RELEASE)
        MainWidget.win = self.load_ui()
        self.threadpool = QThreadPool()
        self.pitch_previous_value = DEFAULT_PITCH

        # default key mapping (matches the key names in the GUI)
        self.pitch_shifted_keys = []
        octave_count = 8

        for octave in range(octave_count):
            for note in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]:
                self.pitch_shifted_keys.append(note + str(octave))


        # MIDI stuff here begins here:
        pygame.midi.init()
        input_device = (
            identify_and_select_midi_device()
        )  # call device detection function once, and store it in Input_device variable

        #handling blurb for no-device situation 
        if input_device is not None:
            # These lines essentially set up the MIDI thread, connect the appropriate method for receiving MIDI input, and start the thread's execution.
            # This allows the application to receive and process MIDI messages concurrently without blocking the main user interface.
    
            # Create an instance of MidiInputWorker
            self.midi_worker = MidiInputWorker(input_device, self)

            # Start the MidiInputWorker as a new thread
            self.threadpool.start(self.midi_worker)

            self.midi_thread = MidiThread(None)
            # self.midi_thread.start_midi_thread.connect(lambda: self.midi_thread.receive_midi_input(input_device))

            # Start the MIDI thread
            self.midi_thread.start()

        else:
                print("No MIDI device selected. Check Connections or Rock the SNAKESynth GUI")  # readout for no MIDI device situation 

            # /end midi stuff
        
        
    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "../ui/form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        win = loader.load(ui_file, self)
        ui_file.close()
        self.set_default_values(win)

        # Connecting knob values to its corresponding spin box values
        win.attack_knob.valueChanged.connect(self.handle_attack_changed)
        win.decay_knob.valueChanged.connect(self.handle_decay_changed)
        win.sustain_knob.valueChanged.connect(self.handle_sustain_changed)
        win.release_knob.valueChanged.connect(self.handle_release_changed)
        win.pitch_knob.valueChanged.connect(self.handle_pitch_changed)
        win.volume_knob.valueChanged.connect(self.handle_volume_changed)

        # Connecting spin box values to its corresponding knob values
        win.attack_double_spin_box.valueChanged.connect(
            self.handle_attack_spin_box_value_changed
        )
        win.decay_double_spin_box.valueChanged.connect(
            self.handle_decay_spin_box_value_changed
        )
        win.sustain_double_spin_box.valueChanged.connect(
            self.handle_sustain_spin_box_value_changed
        )
        win.release_double_spin_box.valueChanged.connect(
            self.handle_release_spin_box_value_changed
        )
        win.pitch_double_spin_box.valueChanged.connect(
            self.handle_pitch_spin_box_value_changed
        )
        win.volume_double_spin_box.valueChanged.connect(
            self.handle_volume_spin_box_value_changed
        )

        # Wave selection mechanism
        win.sine.clicked.connect(lambda: self.handle_waveform_selected("sine"))
        win.square.clicked.connect(lambda: self.handle_waveform_selected("square"))
        win.sawtooth.clicked.connect(lambda: self.handle_waveform_selected("sawtooth"))
        win.triangle.clicked.connect(lambda: self.handle_waveform_selected("triangle"))

        # KEYBOARD KEYS
        # Find all keys in the GUI and assign event handlers to each
        keys = win.keys_frame.findChildren(QPushButton)
        for key in keys:
            note = key.objectName()
            key.pressed.connect(lambda note=note: self.button_pressed_handler(note))
            key.released.connect(self.button_released_handler)

        return win

    def play_loop(self, wav):
        # Deal with stereo.
        channels = 1

        # Set up and start the stream.
        stream = sd.RawOutputStream(
            samplerate=SAMPLE_RATE,
            blocksize=len(wav),
            channels=1,
            dtype="int16",
        )

        # Write the samples.
        stream.start()

        # Continuously apply adsr envelope to samples
        while self.adsr_envelope._state != State.IDLE:
            out_buffer = np.empty(len(wav))
            for i in range(len(wav)):
                out_buffer[i] = self.adsr_envelope.process(wav[i])
            stream.write(self.vol_ctrl.change_gain(out_buffer.astype(np.int16)))

    # Define a method for handling button releases
    def button_pressed_handler(self, key):
        key_mapping = list(zip(GUI_KEY_NAMES, self.pitch_shifted_keys))
        mapped_key = None  # Initialize mapped_key with a default value for MIDI input handling

        for pair in key_mapping:
            if key == pair[0]:
                mapped_key = pair[1]
                break  # exit loop once match is found

        if mapped_key is not None:  # Check if a valid mapped_key value was found
            self.adsr_envelope.update_state(State.ATTACK)
            worker = Worker(self.play_loop, selected_waves[mapped_key])
            self.threadpool.start(worker)

    def button_released_handler(self):
        self.adsr_envelope.update_state(State.RELEASE)

    def set_default_values(self, win):
        # default attack, sustain, release, decay values
        win.attack_knob.setValue(DEFAULT_ATTACK)
        win.attack_double_spin_box.setValue(DEFAULT_ATTACK)
        win.decay_knob.setValue(DEFAULT_DECAY)
        win.decay_double_spin_box.setValue(DEFAULT_DECAY)
        win.sustain_knob.setValue(DEFAULT_SUSTAIN)
        win.sustain_double_spin_box.setValue(DEFAULT_SUSTAIN)
        win.release_knob.setValue(DEFAULT_RELEASE)
        win.release_double_spin_box.setValue(DEFAULT_RELEASE)

        # Set up default value of the volume knob
        win.volume_knob.setValue(DEFAULT_VOLUME)

        # Default wave selection
        win.sine.setChecked(True)
        self.handle_waveform_selected("sine")

        # Default pitch
        win.pitch_knob.setValue(DEFAULT_PITCH)
        win.pitch_double_spin_box.setValue(DEFAULT_PITCH)

    # Handle different wave types
    def handle_waveform_selected(self, selected_waveform):
        global selected_waves
        if selected_waveform == "sine":
            selected_waves = sine_waves
        elif selected_waveform == "square":
            selected_waves = square_waves
        elif selected_waveform == "sawtooth":
            selected_waves = saw_waves
        elif selected_waveform == "triangle":
            selected_waves = triangle_waves

    #
    # Handle knob values changed
    #

    def handle_attack_changed(self, value):
        # Reflect the Attack spin box value as per the current value of the Attack dial
        self.win.attack_double_spin_box.setValue(self.win.attack_knob.value())
        self.adsr_envelope.update_attack(value)

    def handle_decay_changed(self, value):
        # Reflect the Decay spin box value as per the current value of the Decay dial
        self.win.decay_double_spin_box.setValue(self.win.decay_knob.value())
        self.adsr_envelope.update_decay(value)

    def handle_sustain_changed(self, value):
        # Reflect the Sustain spin box value as per the current value of the Sustain dial
        self.win.sustain_double_spin_box.setValue(self.win.sustain_knob.value())
        self.adsr_envelope.update_sustain(value)

    def handle_release_changed(self, value):
        # Reflect the Release spin box value as per the current value of the Release dial
        self.win.release_double_spin_box.setValue(self.win.release_knob.value())
        self.adsr_envelope.update_release(value)

    def handle_pitch_changed(self):
        knob_value = self.win.pitch_knob.value()

        # Only allow the user to use the knob to change the pitch value by one unit
        if (
            knob_value != self.pitch_previous_value + 1
            and knob_value != self.pitch_previous_value - 1
        ):
            self.win.pitch_double_spin_box.setValue(self.pitch_previous_value)
            self.win.pitch_knob.setValue(self.pitch_previous_value)
        else:
            # Reflect the Pitch spin box value as per the current value of the Pitch dial
            self.win.pitch_double_spin_box.setValue(knob_value)

        knob_value = self.win.pitch_knob.value()

        # Calculate the difference between previous knob value and current knob value
        difference = knob_value - self.pitch_previous_value
        self.pitch_previous_value = knob_value

        # update the pitch key list
        for i, key in enumerate(self.pitch_shifted_keys):
            note_name = key[:-1]
            note_octave = int(key[-1])
            new_octave = note_octave+difference
            self.pitch_shifted_keys[i] = f"{note_name}{str(new_octave)}"

    # Whenever the knob is turned, get the new gain coefficient then apply to all keys
    def handle_volume_changed(self):
        knob_value = self.win.volume_knob.value()
        self.win.volume_double_spin_box.setValue(knob_value)
        print(knob_value)
        self.vol_ctrl.config(knob_value)

    #
    # Handle spin box values changed
    #

    def handle_attack_spin_box_value_changed(self):
        # Reflect the Attack dial value as per the current value of the Attack spin box
        self.win.attack_knob.setValue(self.win.attack_double_spin_box.value())

    def handle_decay_spin_box_value_changed(self):
        # Reflect the Decay dial value as per the current value of the Decay spin box
        self.win.decay_knob.setValue(self.win.decay_double_spin_box.value())

    def handle_sustain_spin_box_value_changed(self):
        # Reflect the Sustain dial value as per the current value of the Sustain spin box
        self.win.sustain_knob.setValue(self.win.sustain_double_spin_box.value())

    def handle_release_spin_box_value_changed(self):
        # Reflect the Release dial value as per the current value of the Release spin box
        self.win.release_knob.setValue(self.win.release_double_spin_box.value())

    def handle_pitch_spin_box_value_changed(self):
        # Reflect the Pitch dial value as per the current value of the Pitch spin box
        self.win.pitch_knob.setValue(self.win.pitch_double_spin_box.value())

    def handle_volume_spin_box_value_changed(self):
        # Reflect the Volume dial value as per the current value of the Volume spin box
        self.win.volume_knob.setValue(self.win.volume_double_spin_box.value())
