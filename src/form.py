"""
Overview
This code represents a synthesizer GUI application written in Python using the PySide6 library.
The synthesizer UI supports multiple waveforms including sine, square, sawtooth, and triangle waves
with adjustable parameters attack, decay, sustain, and release (ADSR envelope), volume, pitch, and tone. 

Wave Generation
After defining the constants, the code generates waveforms for each key using different oscillators 
(sine, square, sawtooth, and triangle). These waveforms are stored in dictionaries for easy access.

MainWidget Class
The MainWidget class represents the main widget of the synthesizer application. It inherits from 
the QWidget class provided by the PySide6 library. The class contains methods for handling UI events, 
such as button presses, knob changes, and waveform selection.

ChatGPT was utilized to improve the docstrings in this file.
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
)
from PySide6.QtCore import QFile, QThreadPool
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
from midi_detect import identify_device
from threads import Worker, MidiInputWorker, MidiWorker
import pygame
import sounddevice as sd
import numpy as np
from numpy import ndarray

sd.default.latency = "low"

SAMPLE_RATE: int = 48000
MAX_AMPLITUDE: int = 8192
DEFAULT_DURATION: float = 0.2
DEFAULT_VOLUME: int = 9
DEFAULT_VOLUME_OFFSET: int = 9
DEFAULT_ATTACK: int = 2
DEFAULT_DECAY: int = 7
DEFAULT_SUSTAIN: int = 8
DEFAULT_RELEASE: int = 3
DEFAULT_PITCH: int = 3

"""
turned linting formatting off for this python list.
due to its length, it is much easier to read formatted in this
way instead of the way it would be linted in black
"""
# fmt: off
GUI_KEYS: list[str] = [
    "C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0",
    "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
    "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
    "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
    "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
    "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
    "C6", "C36", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", "A6", "A#6", "B6",
    "C7", "C#7", "D7" ,"D#7", "E7", "F7", "F#7", "G7", "G#7", "A7", "A#7", "B7"
]
# fmt: on

"""
generate an oscillator for each key inside a dictionary
Note: due to saw wave and square wave implementation, 
generating them takes a lot longer, might need rework in the future.
"""
sine_waves: ndarray[np.int16] = {}
square_waves: ndarray[np.int16] = {}
saw_waves: ndarray[np.int16] = {}
triangle_waves: ndarray[np.int16] = {}

for key in NOTE_FREQS:
    sine_waves[key] = sine(
        NOTE_FREQS[key], SAMPLE_RATE, MAX_AMPLITUDE, DEFAULT_DURATION
    ).generate_wave()
    square_waves[key] = square(
        NOTE_FREQS[key], SAMPLE_RATE, MAX_AMPLITUDE, DEFAULT_DURATION
    ).generate_wave()
    saw_waves[key] = saw(
        NOTE_FREQS[key], SAMPLE_RATE, MAX_AMPLITUDE, DEFAULT_DURATION
    ).generate_wave()
    triangle_waves[key] = triangle(
        NOTE_FREQS[key], SAMPLE_RATE, MAX_AMPLITUDE, DEFAULT_DURATION
    ).generate_wave()


class MainWidget(QWidget):
    def __init__(self) -> None:
        """
        Initializes an instance of the MainWidget class, inheriting attributes and methods from QWidget.
        
        Attributes:
        - vol_ctrl (Volume): Manages volume control using a Volume instance.
        - adsr_envelope (ADSREnvelope): Handles ADSR (Attack, Decay, Sustain, Release) envelope parameters.
        - win (QWidget): Loads the UI and assigns it to the MainWidget window.
        - threadpool (QThreadPool): Manages threads for concurrent operations.
        - pitch_previous_value (int): Holds the default pitch value.
        - pitch_shifted_keys (list[str]): Stores default key mappings for the GUI.
        - octave_count (int): Defines the number of octaves for key mappings.
        """
        super(MainWidget, self).__init__()
        self.vol_ctrl: Volume = Volume(DEFAULT_VOLUME, DEFAULT_VOLUME_OFFSET)
        self.adsr_envelope: ADSREnvelope = ADSREnvelope(
            DEFAULT_ATTACK, DEFAULT_DECAY, DEFAULT_SUSTAIN, DEFAULT_RELEASE
        )
        MainWidget.win: QWidget = self.load_ui()
        self.threadpool: QThreadPool = QThreadPool()
        self.pitch_previous_value: int = DEFAULT_PITCH

        # default key mapping (matches the key names in the GUI)
        self.pitch_shifted_keys: list[str] = []
        octave_count: int = 8

        for octave in range(octave_count):
            for note in [
                "C",
                "C#",
                "D",
                "D#",
                "E",
                "F",
                "F#",
                "G",
                "G#",
                "A",
                "A#",
                "B",
            ]:
                self.pitch_shifted_keys.append(note + str(octave))

        self.MIDI_init()

    def MIDI_init(self) -> None:
        """
        Initializes the MIDI functionality for the application.

        This function sets up the MIDI thread, identifying and connecting to the appropriate
        MIDI input device, and starts the thread's execution to enable the application
        to asynchronously receive and process MIDI messages without obstructing the main user interface.
        """
        pygame.midi.init()
        input_device = (
            identify_device()
        )  # return value is either None or the MIDI device
        if input_device is not None:
            self.midi_worker: MidiInputWorker = MidiInputWorker(input_device, self)
            self.threadpool.start(self.midi_worker)
            self.midi_thread: MidiWorker = MidiWorker(None)
            self.midi_thread.start()
        else:
            print(
                "No MIDI device selected. Check Connections or Rock the SNAKESynth GUI"
            )

    def load_ui(self) -> QWidget:
        """
        Loads the graphical user interface (GUI) window and its elements from a designated UI file.
        Utilizes the QUiLoader to load the UI window and its components from the specified file path.
        Returns the generated GUI window after loading.
        Returns:
        QWidget: The generated GUI window populated with elements from the UI file.
        """
        loader: QUiLoader = QUiLoader()
        path: str = os.fspath(Path(__file__).resolve().parent / "../ui/form.ui")
        ui_file: QFile = QFile(path)
        ui_file.open(QFile.ReadOnly)
        win: QWidget = loader.load(ui_file, self)
        ui_file.close()
        self.set_default_values(win)
        self.connect_knob_and_spinbox_values(win)
        self.wave_selection(win)
        self.assign_key_handler(win)
        return win

    def set_default_values(self, win) -> None:
        """
        Sets the default values for each knob on the UI:
        (Attack, Decay, Sustain, Release, Volume, Pitch)
        Sets the default wave selection
        Args:
        win: The UI window object where default values are to be set.
        """
        # attack
        win.attack_knob.setValue(DEFAULT_ATTACK)
        win.attack_double_spin_box.setValue(DEFAULT_ATTACK)
        # decay
        win.decay_knob.setValue(DEFAULT_DECAY)
        win.decay_double_spin_box.setValue(DEFAULT_DECAY)
        # sustain
        win.sustain_knob.setValue(DEFAULT_SUSTAIN)
        win.sustain_double_spin_box.setValue(DEFAULT_SUSTAIN)
        # release
        win.release_knob.setValue(DEFAULT_RELEASE)
        win.release_double_spin_box.setValue(DEFAULT_RELEASE)
        # volume
        win.volume_knob.setValue(DEFAULT_VOLUME)
        win.volume_double_spin_box.setValue(DEFAULT_VOLUME)
        # pitch
        win.pitch_knob.setValue(DEFAULT_PITCH)
        win.pitch_double_spin_box.setValue(DEFAULT_PITCH)
        # wave selection
        win.sine.setChecked(True)
        self.handle_waveform_selected("sine")

    def connect_knob_and_spinbox_values(self, win) -> None:
        """
        Establishes connections between knob and spinbox values in the GUI.

        Args:
        win: The UI window object where knob and spinbox values are to be connected.

        This function sets up bidirectional connections between knob values and their
        corresponding spinbox values in the GUI. Changes in either the knob or spinbox
        will reflect in both components to maintain synchronization.
        """
        # Connecting knob values to its corresponding spin box values
        win.attack_knob.valueChanged.connect(lambda v: self.handle_knob_value_changed("attack", v))
        win.decay_knob.valueChanged.connect(lambda v: self.handle_knob_value_changed("decay", v))
        win.sustain_knob.valueChanged.connect(lambda v: self.handle_knob_value_changed("sustain", v))
        win.release_knob.valueChanged.connect(lambda v: self.handle_knob_value_changed("release", v))
        win.pitch_knob.valueChanged.connect(lambda v: self.handle_knob_value_changed("pitch", v))
        win.volume_knob.valueChanged.connect(lambda v: self.handle_knob_value_changed("volume", v))

        # Connecting spin box values to its corresponding knob values
        win.attack_double_spin_box.valueChanged.connect(
            lambda: self.handle_spin_box_value_changed("attack")
        )
        win.decay_double_spin_box.valueChanged.connect(
            lambda: self.handle_spin_box_value_changed("decay")
        )
        win.sustain_double_spin_box.valueChanged.connect(
            lambda: self.handle_spin_box_value_changed("sustain")
        )
        win.release_double_spin_box.valueChanged.connect(
            lambda: self.handle_spin_box_value_changed("release")
        )
        win.pitch_double_spin_box.valueChanged.connect(
            lambda: self.handle_spin_box_value_changed("pitch")
        )
        win.volume_double_spin_box.valueChanged.connect(
            lambda: self.handle_spin_box_value_changed("volume")
        )

    def wave_selection(self, win) -> None:
        """
        This function sets up connections between the different waveform selection buttons
        on the GUI and the corresponding handler method for selecting different waveforms.
        When a waveform button is clicked, the associated method for waveform selection is triggered.
        Args:
        win: The UI window object providing the waveform selection controls.
        """
        win.sine.clicked.connect(lambda: self.handle_waveform_selected("sine"))
        win.square.clicked.connect(lambda: self.handle_waveform_selected("square"))
        win.sawtooth.clicked.connect(lambda: self.handle_waveform_selected("sawtooth"))
        win.triangle.clicked.connect(lambda: self.handle_waveform_selected("triangle"))

    def assign_key_handler(self, win) -> None:
        """
        This function identifies all the keys within the GUI and assigns event handlers to manage
        key press and release actions for each individual key. The event handlers enable the
        manipulation of musical notes or actions associated with the specific keys.
        Args:
        win: The UI window object containing the keys for which event handlers are being assigned.
        """
        keys = win.keys_frame.findChildren(QPushButton)
        for key in keys:
            note = key.objectName()
            key.pressed.connect(lambda note=note: self.key_pressed_handler(note))
            key.released.connect(self.key_released_handler)

    def key_pressed_handler(self, key) -> None:
        """
        This function handles when a key is pressed.
        First it maps the named keys in the GUI to the
        correct notes defined by the shift in pitch.
        Once the keys are mapped it updates the ADSR state
        and plays the continous wave on one thread.
        Args:
        win: The UI window object containing the keys for which event handlers are being assigned.
        """
        key_mapping = list(zip(GUI_KEYS, self.pitch_shifted_keys))
        mapped_key = (
            None  # Initialize mapped_key with a default value for MIDI input handling
        )
        for pair in key_mapping:
            if key == pair[0]:
                mapped_key = pair[1]
                break  # exit loop once match is found

        if mapped_key is not None:  # Check if a valid mapped_key value was found
            self.adsr_envelope.update_state(State.ATTACK)
            worker = Worker(self.play_loop, selected_waves[mapped_key])
            self.threadpool.start(worker)

    def key_released_handler(self) -> None:
        """
        This function updates the ADSR state when a key is released
        to move into the next portion of envelope.
        """
        self.adsr_envelope.update_state(State.RELEASE)

    def play_loop(self, wav) -> None:
        """
        This function sets up continuous play of the note.
        When a key is pressed, the ADSR envelope is continuously
        applied to the wave passed in. Then volume is appled and
        the wave is output continously so there is no break in
        the output wave.
        Args:
        wav: the wave sent in to be looped
        """
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
            out_buffer: ndarray[np.int16] = np.empty(len(wav))
            for i in range(len(wav)):
                out_buffer[i] = self.adsr_envelope.process(wav[i])
            stream.write(self.vol_ctrl.change_gain(out_buffer.astype(np.int16)))

    def handle_waveform_selected(self, selected_waveform) -> None:
        """
        This function handles when a different waveform is
        selected in the GUI and updates the selected waveform.
        Args:
        selected_waveform: this is the user selected waveform
        """
        global selected_waves
        if selected_waveform == "sine":
            selected_waves = sine_waves
        elif selected_waveform == "square":
            selected_waves = square_waves
        elif selected_waveform == "sawtooth":
            selected_waves = saw_waves
        elif selected_waveform == "triangle":
            selected_waves = triangle_waves

    def handle_pitch_knob_changed(self) -> None:
        """
        This function handles when the pitch knob value is changed.
        """
        knob_value = self.win.pitch_knob.value()
        # User can only change the pitch value by one unit
        if (
            knob_value != self.pitch_previous_value + 1
            and knob_value != self.pitch_previous_value - 1
        ):
            self.win.pitch_double_spin_box.setValue(self.pitch_previous_value)
            self.win.pitch_knob.setValue(self.pitch_previous_value)
        else:
            # Update Pitch spin box
            self.win.pitch_double_spin_box.setValue(knob_value)

        knob_value = self.win.pitch_knob.value()

        # Calculate the difference between previous knob value and current knob value
        difference = knob_value - self.pitch_previous_value

        # update the pitch key list
        for i, key in enumerate(self.pitch_shifted_keys):
            note_name = key[:-1]
            note_octave = int(key[-1])
            new_octave = note_octave + difference
            self.pitch_shifted_keys[i] = f"{note_name}{str(new_octave)}"

    # Whenever the knob is turned, get the new gain coefficient then apply to all keys
    def handle_volume_knob_changed(self) -> None:
        """
        This function handles when the volume knob value is changed.
        """
        # Update Volume spin box
        knob_value = self.win.volume_knob.value()
        self.win.volume_double_spin_box.setValue(knob_value)
        self.vol_ctrl.config(knob_value)

    def handle_knob_value_changed(self, spin_box: str, value: float) -> None:
        """
        This function handles synchronizing the values between spin box
        and a knob when the knob value changes.
        """
        match spin_box:
            case "attack":
                self.win.attack_double_spin_box.setValue(self.win.attack_knob.value())
                self.adsr_envelope.update_attack(value) 
                return
            case "decay":
                self.win.decay_double_spin_box.setValue(self.win.decay_knob.value())
                self.adsr_envelope.update_decay(value)
                return
            case "sustain":
                self.win.sustain_double_spin_box.setValue(self.win.sustain_knob.value())
                self.adsr_envelope.update_sustain(value)
                return
            case "release":
                self.win.release_double_spin_box.setValue(self.win.release_knob.value())
                self.adsr_envelope.update_release(value)
                return
            case "pitch":
                self.handle_pitch_knob_changed()
                return
            case "volume":
                self.handle_volume_knob_changed()
                return
            case _:
                raise "spin box not found for: " + spin_box

    def handle_spin_box_value_changed(self, knob: str) -> None:
        """
        This function handles synchronizing the values between a spin box
        and a knob when the spin box value changes.
        """
        match knob:
            case "attack":
                self.win.attack_knob.setValue(self.win.attack_double_spin_box.value())
                return
            case "decay":
                self.win.decay_knob.setValue(self.win.decay_double_spin_box.value())
                return
            case "sustain":
                self.win.sustain_knob.setValue(self.win.sustain_double_spin_box.value())
                return
            case "release":
                self.win.release_knob.setValue(self.win.release_double_spin_box.value())
                return
            case "pitch":
                self.win.pitch_knob.setValue(self.win.pitch_double_spin_box.value())
                return
            case "volume":
                self.win.volume_knob.setValue(self.win.volume_double_spin_box.value())
                return
            case _:
                raise "knob not found for: " + knob