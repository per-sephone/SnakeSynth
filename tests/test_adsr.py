import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adsr import ADSREnvelope
import numpy as np
import pytest


@pytest.fixture
def sample_wave():
    t = np.linspace(0, 2.0, int(48000 * 2.0), endpoint=False)
    return 0.5 * np.sin(2.0 * np.pi * 440.0 * t)


def test_apply_envelope(sample_wave):
    # Create an instance of ADSREnvelope
    envelope = ADSREnvelope(sample_wave)

    # Check if the envelope has been applied correctly
    assert len(envelope._envelope) == len(sample_wave)
    assert len(envelope._modulated_wave) == len(sample_wave)

    # Check if the envelope has been applied correctly
    attack_samples = int(envelope._attack * envelope._sample_rate)
    decay_samples = int(envelope._decay * envelope._sample_rate)
    release_samples = int(envelope._release * envelope._sample_rate)
    sustain_samples = (
        len(sample_wave) - attack_samples - decay_samples - release_samples
    )

    expected_envelope = np.concatenate(
        (
            np.linspace(0, 1, attack_samples),
            np.linspace(1, envelope._sustain, decay_samples),
            np.full((sustain_samples,), envelope._sustain),
            np.linspace(envelope._sustain, 0, release_samples),
        )
    )

    assert np.array_equal(envelope._envelope, expected_envelope)

    normalized_wave = sample_wave / np.max(np.abs(sample_wave))
    assert np.array_equal(envelope._modulated_wave, normalized_wave * expected_envelope)


def test_apply_envelope_with_custom_parameters(sample_wave):
    # Create an instance of ADSREnvelope with custom parameters
    envelope = ADSREnvelope(
        sample_wave,
        attackDuration=0.1,
        decayDuration=0.3,
        sustainLevel=0.5,
        releaseDuration=0.4,
    )

    # Check if the envelope has been applied correctly
    assert len(envelope._envelope) == len(sample_wave)
    assert len(envelope._modulated_wave) == len(sample_wave)

    # Check if the envelope has been applied correctly
    attack_samples = int(envelope._attack * envelope._sample_rate)
    decay_samples = int(envelope._decay * envelope._sample_rate)
    release_samples = int(envelope._release * envelope._sample_rate)
    sustain_samples = (
        len(sample_wave) - attack_samples - decay_samples - release_samples
    )

    expected_envelope = np.concatenate(
        (
            np.linspace(0, 1, attack_samples),
            np.linspace(1, envelope._sustain, decay_samples),
            np.full(sustain_samples, envelope._sustain),
            np.linspace(envelope._sustain, 0, release_samples),
        )
    )

    assert np.array_equal(envelope._envelope, expected_envelope)

    normalized_wave = sample_wave / np.max(np.abs(sample_wave))
    assert np.array_equal(envelope._modulated_wave, normalized_wave * expected_envelope)


def test_default_sample_rate(sample_wave):
    # Create an instance of ADSREnvelope with the default sample rate
    envelope = ADSREnvelope(sample_wave)

    # Check if the sample rate is set to the default value of 48000
    assert envelope._sample_rate == 48000
