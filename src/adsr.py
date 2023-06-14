'''Design inspired by 
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

'''

import numpy as np
import enum
import sounddevice as sd

DEFAULT_MS = 0.05

class State(enum.Enum):
    IDLE = 0
    ATTACK = 1
    DECAY = 2
    SUSTAIN = 3
    RELEASE = 4

import numpy as np
class ADSREnvelope:
    def __init__(self, attack_duration=.5, decay_duration=1, sustain_level=1, release_duration=1, sample_rate=48000):
        self._sample_rate = sample_rate
        self._state = State.IDLE
        self._pos = 0

        self._attack_samples = int(attack_duration * DEFAULT_MS * sample_rate)
        self._decay_samples = int(decay_duration * DEFAULT_MS * sample_rate)
        self._sustain = sustain_level * DEFAULT_MS
        self._release_samples = int(release_duration * DEFAULT_MS * sample_rate)

        self._envelope = np.zeros(sample_rate) #empty envelope
        self._attack_env = self.create_attack_envelope()
        self._decay_env = self.create_decay_envelope()
        self._release_env = self.create_release_envelope()

    def update_state(self, state):
        self._pos = 0
        self._state = state

    def update_attack(self, attack):
        self._attack_samples = int(attack * DEFAULT_MS * self._sample_rate)
        self._attack_env = self.create_attack_envelope()
    
    def update_decay(self, decay):
        self._decay_samples = int(decay * DEFAULT_MS * self._sample_rate)
        self._decay_env = self.create_decay_envelope()
    
    def update_sustain(self, sustain):
        self._sustain = sustain * DEFAULT_MS
        
    def update_release(self, release):
        self._release_samples = int(release * DEFAULT_MS * self._sample_rate)
        self._release_env = self.create_release_envelope()

    def process(self, sample):
        #takes in a sample, process based on state, return sample with envelope applied
        try:
            if self._state == State.ATTACK:
                output = sample * self._attack_env[self._pos]
                self._pos += 1
                if self._pos >= self._attack_samples:
                    self.update_state(State.DECAY)
                return output
            
            elif self._state == State.DECAY:
                output = sample * self._decay_env[self._pos]
                self._pos += 1
                if self._pos >= self._decay_samples:
                    self.update_state(State.SUSTAIN)
                return output
            
            elif self._state == State.SUSTAIN:
                return sample *  self._sustain
            
            elif self._state == State.RELEASE:
                output = sample * self._release_env[self._pos]
                self._pos += 1
                if self._pos >= self._release_samples:
                    self.update_state(State.IDLE)
                return output
            else:
                return 0
            
        except IndexError:          #if knob is turned to 0 
            return          #return without applying that part of the envelope
        
    def create_attack_envelope(self):
        return np.linspace(0,1,self._attack_samples)
    
    def create_decay_envelope(self):
        return np.linspace(1,self._sustain,self._decay_samples)
    
    def create_release_envelope(self):
        return np.linspace(self._sustain,0,self._release_samples)

