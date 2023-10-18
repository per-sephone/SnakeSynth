'''Design inspired by 
https://python.plainenglish.io/build-your-own-python-synthesizer-part-2-66396f6dad81

Some code utilized from Tone homework including code provided by Bart Massey

The Tone class represents the filter control typically found in synthesizers. This class contains 3 filters for
low end, mid range, and treble. The knob values control how loud each respective filter is compared to the others. 
Users can use a combination of knob configuration to alter the sound of a given sound.

To use the Tone class, follow these steps:

1. Create an instance of the Tone class and specify the knob value of each filter, the first frequency the the bass and mid filter, 
the second frequency for the mid and treble filter.
2. Call the 3 setters (set_bass, set_mid, set_treble) to update the knob_value and apply the filter.
3. Call filter with an np array of samples, which gives back a filtered sound wave with all three filters
'''

from scipy import io, signal
import numpy as np

DEFAULT_GAIN = 1.0
DEFAULT_KNOB_VAL = 5

class Tone():
    def __init__(self, bass_knob=DEFAULT_KNOB_VAL, mid_knob=DEFAULT_KNOB_VAL, treble_knob=DEFAULT_KNOB_VAL, first_stop=300, second_stop=4000, rate=48000):
        self._first_stop = first_stop
        self._second_stop = second_stop
        self._rate = rate

        self._bass_filter = Filter(type='lowpass', rate=rate, knob_value=bass_knob, splits=[first_stop] )
        self._mid_filter = Filter(type='bandpass', rate=rate, knob_value=mid_knob, splits=[first_stop, second_stop])
        self._treble_filter = Filter(type='highpass', rate=rate, knob_value=treble_knob, splits=[second_stop])

    def set_bass(self, knob_value):
        self._bass_filter.config(knob_value)

    def set_mid(self, knob_value):
        self._mid_filter.config(knob_value)

    def set_treble(self, knob_value):
        self._treble_filter.config(knob_value)

    def filter(self, samples):
        low_passed = self._bass_filter.filter(samples)
        band_passed = self._mid_filter.filter(samples)
        high_passed = self._treble_filter.filter(samples)

        return low_passed + band_passed + high_passed


class Filter():
    def __init__(
        self,
        type='lowpass',
        rate=48000,
        knob_value=DEFAULT_KNOB_VAL,
        splits = [300]
    ):
        self._type = type
        self._rate: float = rate
        self._knob_value = knob_value
        self._splits = splits
        self._gain = DEFAULT_GAIN
        self._coeff = self.generate_coeff()

    #Build filters coefficients
    def generate_coeff(self):
        print(self._type)
        print(self._rate)
        print(self._splits)
        print(self._gain)
        freqs = 2.0 * np.array(self._splits, dtype=np.float64) / self._rate
        return signal.firwin(255, freqs, pass_zero=self._type)
    
    #Filter sound wave
    def filter(self, samples):
        return signal.lfilter(self._coeff, [1],  samples) * self._gain


    #set gain
    def config(self, knob_value):
        self._knob_value = knob_value
        self._gain = self.tone_gain_converter(knob_value)
        print(self._gain)

    # Convert from knob value to gain value for tone
    def tone_gain_converter(self, knob_value, offset=5):
        if knob_value < 1:
            return 0
        db = 3.0 * (knob_value - offset)
        return pow(10.0, db / 20.0)

