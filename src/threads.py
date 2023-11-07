from PySide6.QtCore import QObject, QRunnable, Slot, Signal
import pygame
from midi_detect import receive_input

#Thread Worker
class Worker(QRunnable):
    """
    The Worker class is a helper class used to execute audio processing tasks in a separate thread, preventing GUI
    blocking while running these tasks.

    This class extends the QRunnable class, making it suitable for use with Qt's concurrent framework for concurrent
    execution.

    Args:
        fn (callable): The function to be executed in the separate thread.
        *args: Positional arguments to be passed to the function.
        **kwargs: Keyword arguments to be passed to the function.
    """
    def __init__(self, fn, *args, **kwargs) -> None:
        """
        Initialize a Worker instance.

        Args:
            fn (callable): The function to be executed in the separate thread.
            *args: Positional arguments to be passed to the function.
            **kwargs: Keyword arguments to be passed to the function.
        """
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()  # QtCore.Slot
    def run(self) -> None:
        """
        Execute the specified function in a separate thread.

        This method is automatically called when the Worker is started within a QThreadPool.
        It runs the specified function with the provided arguments.
        """
        self.fn(self.args[0])
class MidiWorker(QObject):
    """
    The MidiWorker class manages MIDI input functionality in a separate thread.

    This class is responsible for initializing the MIDI system using `pygame.midi.init()` and defining a signal named
    `start_midi_thread`. It is designed to work with the `MidiInputWorker` class to receive and process MIDI messages
    concurrently without blocking the main user interface.

    Attributes:
        signal (Signal): A signal used to trigger the MIDI processing thread.

    Args:
        input_device: The MIDI input device to be used for MIDI message reception.

    Note:
    Ensure that you have properly initialized the Pygame MIDI system before using this class.
    """
    pygame.midi.init()
    signal: Signal = Signal()  # establishes a signal to manipulate

    def __init__(self, input_device) -> None:
        """
        Initialize a MidiWorker instance.

        Args:
            input_device: The MIDI input device to be used for MIDI message reception.
        """
        super().__init__()
        pygame.midi.init()
        self.input_device = input_device

    def start(self) -> None:
        """
        Start the MIDI processing thread by emitting the `start_midi_thread` signal.
        """
        self.signal.emit()

class MidiInputWorker(QRunnable):
    """
    The MidiInputWorker class is part of a synthesizer GUI application written in Python using the PySide6 library.

    This class is responsible for handling MIDI input messages and connecting them to the generation of tones in the
    synthesizer.

    Args:
        input_device: The MIDI input device used to receive MIDI messages.
        main_widget: The main widget of the synthesizer GUI application.
    """
    def __init__(self, input_device, main_widget) -> None:
        """
        Initialize a MidiInputWorker instance.

        Args:
            input_device: The MIDI input device used to receive MIDI messages.
            main_widget: The main widget of the synthesizer GUI application.
        """
        super(MidiInputWorker, self).__init__()

        self.input_device = input_device
        self.main_widget = main_widget

    @Slot()
    def run(self) -> None:
        """
        Run the MIDI input processing loop.

        This method continuously processes incoming MIDI messages, specifically note-on and note-off messages.
        When a note-on message is received, it triggers the generation of a tone in the synthesizer based on the
        note value. When a note-off message is received, it releases the previously played tone.
        """
        for msg in receive_input(self.input_device):
            if msg["status"] == 144:  # This is the note on message
                note_value = msg["note"]
                if note_value >= 12 and note_value < 122:
                    try:
                        note_name: str = self.main_widget.pitch_shifted_keys[note_value - 24]
                        print("MIDI KEY NOTE PLAYED:", note_name)
                        self.main_widget.button_pressed_handler(note_name)
                    except IndexError:
                        print("Note value is out of range. Ignoring MIDI message.")

            elif msg["status"] == 128:  # note off message
                self.main_widget.button_released_handler()
