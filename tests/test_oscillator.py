import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.oscillator import SineOscillator
import numpy as np


def test_sine_oscillator():
    freq = 440
    sample_rate = 48000
    duration = 1.0
    oscillator = SineOscillator(
        frequency=freq, sample_rate=sample_rate, duration=duration
    )
    wave = oscillator.generate_wave()
    assert len(wave) == sample_rate * duration
