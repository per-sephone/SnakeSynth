import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adsr import ADSREnvelope
import numpy as np
import pytest

DEFAULT_ATTACK: int = 2
DEFAULT_DECAY: int = 7
DEFAULT_SUSTAIN: int = 8
DEFAULT_RELEASE: int = 3
DEFAULT_MS: float = 0.05


def test_apply_envelope():
    # Create an instance of ADSREnvelope
    envelope = ADSREnvelope(
        DEFAULT_ATTACK, DEFAULT_DECAY, DEFAULT_SUSTAIN, DEFAULT_RELEASE
    )

    # # Check if the envelopes have been created correctly
    attack_samples = envelope._attack_samples
    decay_samples = envelope._decay_samples
    release_samples = envelope._release_samples

    expected_attack_envelope = np.linspace(0, 1, attack_samples)
    expected_decay_envelope = np.linspace(1, envelope._sustain, decay_samples)
    expected_release_envelope = np.linspace(envelope._sustain, 0, release_samples)

    assert np.array_equal(envelope._attack_envelope, expected_attack_envelope)
    assert np.array_equal(envelope._decay_envelope, expected_decay_envelope)
    assert np.array_equal(envelope._release_envelope, expected_release_envelope)


def test_apply_envelope_with_custom_parameters():
    # Create an instance of ADSREnvelope with custom parameters
    envelope = ADSREnvelope(
        attack_duration=0.1,
        decay_duration=0.3,
        sustain_level=0.5,
        release_duration=0.4,
    )

    # Check if the envelopes have been created correctly
    attack_samples = envelope._attack_samples
    decay_samples = envelope._decay_samples
    release_samples = envelope._release_samples

    expected_attack_envelope = np.linspace(0, 1, attack_samples)
    expected_decay_envelope = np.linspace(1, envelope._sustain, decay_samples)
    expected_release_envelope = np.linspace(envelope._sustain, 0, release_samples)
    expected_attack_envelope = np.linspace(0, 1, attack_samples)

    assert np.array_equal(envelope._attack_envelope, expected_attack_envelope)
    assert np.array_equal(envelope._decay_envelope, expected_decay_envelope)
    assert np.array_equal(envelope._release_envelope, expected_release_envelope)


def test_default_sample_rate():
    # Create an instance of ADSREnvelope with the default sample rate
    envelope = ADSREnvelope(
        DEFAULT_ATTACK, DEFAULT_DECAY, DEFAULT_SUSTAIN, DEFAULT_RELEASE
    )

    # Check if the sample rate is set to the default value of 48000
    assert envelope._sample_rate == 48000
