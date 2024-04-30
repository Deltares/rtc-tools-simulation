"""Module for testing the spillway model"""
from pathlib import Path

import numpy as np
import numpy.testing
from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"


class SpillwayModel(ReservoirModel):
    """Class for simulating a spillway model."""

    def apply_schemes(self):
        """Always apply spillway."""
        self.apply_spillway()


def test_spillway():
    """Test the spillway model."""
    config = ModelConfig(base_dir=BASE_DIR)
    model = SpillwayModel(config)
    model.simulate()
    output = model.extract_results()
    v = np.array(output["V"])
    v_ref = np.array([1.3, 0.8, 1.2])
    numpy.testing.assert_array_almost_equal(v, v_ref, decimal=3)
