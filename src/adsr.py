"""Design inspired by 
https://python.plainenglish.io/build-your-own-python-synthesizer-part-2-66396f6dad81

The ADSREnvelope class represents an Attack-Decay-Sustain-Release (ADSR) envelope used in 
a synthesizer. This envelope is responsible for modulating the amplitude of the synthesized 
waveform over time, creating dynamic changes in the sound.

To use the ADSREnvelope class, follow these steps:

1. Create an instance of the ADSREnvelope class, specifying the parameters of 
attack, decay, sustain, release durations, and sample rate.
2. Update the envelope state using the update_state() method to set the initial state.
3. Optionally, dynamically update the attack, decay, sustain, or release parameters using the corresponding 
update methods (update_attack(), update_decay(), update_sustain(), update_release()).
4. Process each sample of the audio waveform by passing it to the process() method, which 
applies the envelope based on the current state and returns the output sample with the envelope applied.

"""

import numpy as np
import numpy.typing as npt
import enum
import sounddevice as sd # type: ignore

DEFAULT_MS: float = 0.05


class State(enum.Enum):
    IDLE = 0
    ATTACK = 1
    DECAY = 2
    SUSTAIN = 3
    RELEASE = 4


import numpy as np


class ADSREnvelope:
    """
    The Attack-Decay-Sustain-Release (ADSR) envelope class is responsible for 
    shaping the parameters of the sound.

    Attributes:
        attack_duration: the time it takes for a sound to reach full volume.
        decay_duration: the time it takes to reach the sustain level.
        sustain_level: the level at which a sound is held.
        release_duration: the time it takes for a sound to gradually fade.
        sample_rate: speed that samples are loaded in cycles per second (hertz)
    """

    def __init__(
        self,
        attack_duration: float = 0.5,
        decay_duration: int = 1,
        sustain_level: int = 1,
        release_duration: int = 1,
        sample_rate: int = 48000,
    ) -> None:
        self._sample_rate = sample_rate
        self._state: State = State.IDLE
        self._pos: int = 0

        self._attack_samples: int = int(attack_duration * DEFAULT_MS * sample_rate)
        self._decay_samples: int = int(decay_duration * DEFAULT_MS * sample_rate)
        self._sustain: float = sustain_level * DEFAULT_MS
        self._release_samples: int = int(release_duration * DEFAULT_MS * sample_rate)

        self._envelope: npt.NDArray[np.float64] = np.zeros(sample_rate)  # empty envelope
        self._attack_envelope: npt.NDArray[np.float64] = self.create_attack_envelope()
        self._decay_envelope: npt.NDArray[np.float64] = self.create_decay_envelope()
        self._release_envelope: npt.NDArray[np.float64] = self.create_release_envelope()

    def update_state(self, state: State) -> None:
        """updates the current ADSR state"""
        self._pos = 0
        self._state = state

    def update_attack(self, attack_duration: float) -> None:
        """update the attack samples and recreate the attack envelope"""
        self._attack_samples = int(attack_duration * DEFAULT_MS * self._sample_rate)
        self._attack_envelope = self.create_attack_envelope()

    def update_decay(self, decay_duration: int) -> None:
        """update the decay samples and recreate the decay envelope"""
        self._decay_samples = int(decay_duration * DEFAULT_MS * self._sample_rate)
        self._decay_envelope = self.create_decay_envelope()

    def update_sustain(self, sustain_level: int) -> None:
        """recalculate and update the sustain"""
        self._sustain = sustain_level * DEFAULT_MS

    def update_release(self, release_duration: int) -> None:
        """update the release samples and recreate the release envelope"""
        self._release_samples = int(release_duration * DEFAULT_MS * self._sample_rate)
        self._release_envelope = self.create_release_envelope()

    def process(self, sample: np.int16) -> float | None:
        """takes in a sample, process based on state, return sample with envelope applied"""
        try:
            output: float = 0
            if self._state == State.ATTACK:
                output = sample * self._attack_envelope[self._pos]
                self._pos += 1
                if self._pos >= self._attack_samples:
                    self.update_state(State.DECAY)
                return output

            elif self._state == State.DECAY:
                output = sample * self._decay_envelope[self._pos]
                self._pos += 1
                if self._pos >= self._decay_samples:
                    self.update_state(State.SUSTAIN)
                return output

            elif self._state == State.SUSTAIN:
                return float(sample * self._sustain)

            elif self._state == State.RELEASE:
                output = sample * self._release_envelope[self._pos]
                self._pos += 1
                if self._pos >= self._release_samples:
                    self.update_state(State.IDLE)
                return output
            else:
                return output

        except IndexError:  # if knob is turned to 0
            return None  # return without applying that part of the envelope


    def create_attack_envelope(self) -> npt.NDArray[np.float64]:
        """
        Create an array of evenly spaced numbers from 0 to 1 
        with the attack sample as the step
        """
        return np.linspace(0, 1, self._attack_samples)

    def create_decay_envelope(self) -> npt.NDArray[np.float64]:
        """
        Create an array of evenly spaced numbers from 1 to the sustain
        with the decay sample as the step
        """
        return np.linspace(1, self._sustain, self._decay_samples)

    def create_release_envelope(self) -> npt.NDArray[np.float64]:
        """
        Create an array of evenly spaced numbers from the sustain to 0
        with the release sample as the step
        """
        return np.linspace(self._sustain, 0, self._release_samples)
