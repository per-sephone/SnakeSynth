'''Design idea from:
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

'''

from abc import ABC
import numpy as np

class Oscillator(ABC):
    def __init__(
        self,
        frequency=220.0,
        sample_rate=48000,
        amplitude=np.iinfo(np.int16).max / 4,
        duration=1.0,
    ):
        self._frequency: float = frequency
        self._sample_rate: int = sample_rate
        self._amplitude: float = amplitude
        self._duration: float = duration
        self._step_size: float = 2.0 * np.pi * self._frequency / sample_rate
        self._time = np.arange(int(self._sample_rate * self._duration))

    def generate_wave(self):
        pass

    # Crop the samples to the final zero crossing, so that the end of a wave match up with the beginning
    # Side effects: final signal is very slightly shorter.
    def crop_samples(self, samples):
        samples_per_period = self._sample_rate / self._frequency
        remainder = round(self._time.size % samples_per_period)

        return samples[0 : self._time.size - remainder]

# SINE OSCILLATOR
class SineOscillator(Oscillator):
    def __init__(
        self,
        frequency=440,
        sample_rate=48000,
        amplitude=np.iinfo(np.int16).max / 4,
        duration=1.0,
    ):
        super().__init__(
            frequency=frequency,
            sample_rate=sample_rate,
            amplitude=amplitude,
            duration=duration,
        )

    def generate_wave(self):
        samples = self._amplitude * np.sin(self._step_size * self._time)
        return self.crop_samples(samples).astype(np.int16)


class SquareOscillator(SineOscillator):
    def __init__(
        self,
        frequency=440,
        sample_rate=48000,
        amplitude=np.iinfo(np.int16).max / 4,
        duration=1.0,
    ):
        super().__init__(
            frequency=frequency,
            sample_rate=sample_rate,
            amplitude=amplitude,
            duration=duration,
        )

    def generate_wave(self):
        samples = np.sin(self._step_size * self._time)
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
        frequency=440,
        sample_rate=48000,
        amplitude=np.iinfo(np.int16).max / 4,
        duration=1.0,
    ):
        super().__init__(
            frequency=frequency,
            sample_rate=sample_rate,
            amplitude=amplitude,
            duration=duration,
        )

    def generate_wave(self):
        samples = np.empty(int(self._sample_rate * self._duration), dtype=float)

        # half-period
        hp = (1 / self._frequency) / 2

        # double the amplitude
        da = self._amplitude * 2

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
        frequency=440,
        sample_rate=48000,
        amplitude=np.iinfo(np.int16).max / 4,
        duration=1.0,
    ):
        super().__init__(
            frequency=frequency,
            sample_rate=sample_rate,
            amplitude=amplitude,
            duration=duration,
        )
        
    def generate_wave(self):
        samples = np.arange(self._sample_rate * self._duration)

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
