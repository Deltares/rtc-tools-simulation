"""Module for testing the adjust model"""
from pathlib import Path

import numpy as np
from numpy.testing import assert_array_almost_equal

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

adjust_dir = Path(__file__).parent.resolve() / "adjust"


class AdjustModel(ReservoirModel):
    """Class for simulating a model with an adjust scheme."""

    def apply_schemes(self):
        """Always adjust volume H to H_observed."""
        self.apply_adjust()


def test_adjust():
    """Test the adjust model. Test for both volume to be correct"""
    config = ModelConfig(base_dir=adjust_dir)
    model = AdjustModel(config)
    model.simulate()
    results = model.extract_results()
    h_ref = np.array([5, 4, 3, 3])
    q_out_ref = np.array([0, 3, 3, 0])
    assert_array_almost_equal(results["Q_out"], q_out_ref)
    assert_array_almost_equal(results["H"], h_ref)
