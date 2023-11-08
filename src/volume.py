# This class handles volume processing for the GUI in form.py
# It contains a default value, and current value, from which the gain coefficient
# can be computed.
# The change_gain method will take a signal and returned an amplified version.

"""
The Volume class allows for changing the volume level and applying gain coefficients to audio signals. 
To use it, import the class, create an instance, use the config() method to configure the volume parameter
given a knob value, use the calculate_gain() method to calculate the gain coefficients, 
and the change_gain() method to dynamically adjust the gain.
"""
import numpy as np
import numpy.typing as npt


class Volume:
    """
    Allows for changing the volume level and applying gain coefficients to audio signals.

    Attributes:
        volume_level: level of the audio signal
        offset: reference point for the volume control
    """

    def __init__(self, volume_level: int = 9, offset: int = 9) -> None:
        self._volume_level = volume_level
        self._offset = offset
        self._gain: float = self.calculate_gain()

    def config(self, volume_level: int) -> None:
        """
        configure all volume parameter given a knob value.
        """
        self._volume_level = volume_level
        self._gain = self.calculate_gain()

    def calculate_gain(self) -> float:
        """
        calculate the gain coefficient based on default offset and current knob
        volume level setting.
        """
        if self._volume_level < 0.1:
            return 0
        decibels: float = 3.0 * (self._volume_level - self._offset)
        return pow(10.0, decibels / 20.0)

    def change_gain(self, samples: npt.NDArray[np.int16]) -> npt.NDArray[np.int16]:
        """
        change the gain of a given sound wave.
        """
        return (samples * self._gain).astype(np.int16)
