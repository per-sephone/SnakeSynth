"""Design idea from:
https://python.plainenglish.io/making-a-synth-with-python-oscillators-2cb8e68e9c3b

The provided code defines four different types of oscillators: SineOscillator, SquareOscillator, 
TriangleOscillator, and SawtoothOscillator. Each oscillator generates a specific waveform and 
provides methods for generating and playing audio waves. The Oscillator class is an abstract
base class which each oscillator pulls common functionality from.

Usage
To use the oscillators in your project, follow these steps:

1. Import the desired oscillator class(es) from the oscillators module.
2. Create an instance of the desired oscillator class, optionally specifying custom parameters 
such as frequency, sample rate, amplitude, and duration.
3. Call the generate_wave() method to generate the audio wave.
4. Optionally, you can call the play() method to play the generated wave using the default audio output device.
5. To stop the audio playback, call the stop() method.

"""

from abc import ABC
import numpy as np


class Oscillator(ABC):
    """
    Oscillator is an abstract base class that implements common functionality for
    concrete oscillator implementations.

    Methods:
        __init__: constructor
        generate_wave: abstract method for generating wave
        crop_samples: method for cropping wave
    """

    def __init__(
        self,
        frequency: float = 220.0,
        sample_rate: int = 48000,
        amplitude: float = np.iinfo(np.int16).max / 4,
        duration: float = 1.0,
    ) -> None:
        """
        Initialization for common oscillator properties
        Extend to create a custom oscillator

        Args:
            frequency: the frequency of the oscillator (note)
            sample_rate: the sample rate (combines with frequency to determine step size)
            amplitude: the amplitude of the oscillator (volume)
            duration: the duration of the oscillator (combines with sample rate to determine time)
        """

        self._frequency: float = frequency
        self._sample_rate: int = sample_rate
        self._amplitude: float = amplitude
        self._duration: float = duration
        self._step_size: float = 2.0 * np.pi * self._frequency / sample_rate
        self._time: np.ndarray = np.arange(int(self._sample_rate * self._duration))

    def generate_wave(self) -> np.ndarray:
        """
        override to generate a wave from the settings established
        upon construction.
        """

        pass

    def crop_samples(self, samples: np.ndarray) -> np.ndarray:
        """
        This function crops the samples to the final zero crossing,
        so the end of a wave matches up with the beginning.
        Side effects: final signal is very slightly shorter.

        Args:
            samples: wave to be trimmed

        Returns:
            a trimmed wave
        """

        samples_per_period: float = self._sample_rate / self._frequency
        remainder: int = round(self._time.size % samples_per_period)

        return samples[0 : self._time.size - remainder]


# SINE OSCILLATOR
class SineOscillator(Oscillator):
    def __init__(
        self,
        frequency: float = 440.0,
        sample_rate: int = 48000,
        amplitude: float = np.iinfo(np.int16).max / 4,
        duration: float = 1.0,
    ) -> None:
        """Extends Oscillator.__init__"""

        super().__init__(
            frequency=frequency,
            sample_rate=sample_rate,
            amplitude=amplitude,
            duration=duration,
        )

    def generate_wave(self) -> np.ndarray:
        """Generates a sine wave"""

        samples: np.ndarray = self._amplitude * np.sin(self._step_size * self._time)
        return self.crop_samples(samples).astype(np.int16)


class SquareOscillator(SineOscillator):
    def __init__(
        self,
        frequency: float = 440.0,
        sample_rate: int = 48000,
        amplitude: float = np.iinfo(np.int16).max / 4,
        duration: float = 1.0,
    ) -> None:
        """Extends Oscillator.__init__"""

        super().__init__(
            frequency=frequency,
            sample_rate=sample_rate,
            amplitude=amplitude,
            duration=duration,
        )

    def generate_wave(self) -> np.ndarray:
        """Generates a square wave"""

        samples: np.ndarray = np.sin(self._step_size * self._time)
        for x in self._time:
            if samples[x] >= 0:
                samples[x] = self._amplitude
            else:
                samples[x] = -self._amplitude

        return self.crop_samples(samples).astype(np.int16)


# TRIANGLE OSCILLATOR
# Source: https://stackoverflow.com/questions/1073606/is-there-a-one-line-function-that-generates-a-triangle-wave
class TriangleOscillator(Oscillator):
    def __init__(
        self,
        frequency: float = 440.0,
        sample_rate: int = 48000,
        amplitude: float = np.iinfo(np.int16).max / 4,
        duration: float = 1.0,
    ) -> None:
        """Extends Oscillator.__init__"""

        super().__init__(
            frequency=frequency,
            sample_rate=sample_rate,
            amplitude=amplitude,
            duration=duration,
        )

    def generate_wave(self) -> np.ndarray:
        """Generates a triangle wave"""

        samples: np.ndarray = np.empty(
            int(self._sample_rate * self._duration), dtype=float
        )

        # half-period
        hp: float = (1 / self._frequency) / 2

        # double the amplitude
        da: float = self._amplitude * 2

        for x in self._time:
            samples[x] = (
                da
                / hp
                * (hp - np.abs(np.mod(x / self._sample_rate + hp / 2, (2 * hp)) - hp))
                - self._amplitude
            )

        return self.crop_samples(samples).astype(np.int16)


# SAW TOOTH OSCILLATOR
class SawtoothOscillator(Oscillator):
    def __init__(
        self,
        frequency: float = 440.0,
        sample_rate: int = 48000,
        amplitude: float = np.iinfo(np.int16).max / 4,
        duration: float = 1.0,
    ) -> None:
        """Extends Oscillator.__init__"""

        super().__init__(
            frequency=frequency,
            sample_rate=sample_rate,
            amplitude=amplitude,
            duration=duration,
        )

    def generate_wave(self) -> np.ndarray:
        """Generates a sawtooth wave"""

        samples: np.ndarray = np.arange(self._sample_rate * self._duration)

        for x in self._time:
            samples[x] = (
                2
                * np.fmod(
                    ((x * self._frequency * self._amplitude) / self._sample_rate)
                    + self._amplitude / 2,
                    self._amplitude,
                )
                - self._amplitude
            )

        return self.crop_samples(samples).astype(np.int16)
