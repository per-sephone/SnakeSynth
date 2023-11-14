import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.volume import Volume


@pytest.fixture
def volume_instance():
    return Volume()


def test_gain(volume_instance):
    volume_instance._volume_level = 0.1
    assert volume_instance.calculate_gain() == pytest.approx(0.0462381021)
    volume_instance._volume_level = 0.5
    assert volume_instance.calculate_gain() == pytest.approx(0.0530884444)
    volume_instance._volume_level = 0.01
    assert volume_instance.calculate_gain() == pytest.approx(0)
    volume_instance._volume_level = 9.0
    assert volume_instance.calculate_gain() == pytest.approx(1.0)
    volume_instance._volume_level = 0.01
    volume_instance._offset = 3.0
    assert volume_instance.calculate_gain() == pytest.approx(0)


def test_volume_initialization(volume_instance):
    assert volume_instance._volume_level == 9
    assert volume_instance._offset == 9
    assert volume_instance._gain == pytest.approx(1.0)
