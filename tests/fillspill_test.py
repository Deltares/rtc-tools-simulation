"""Module for testing the passflow scheme."""
from pathlib import Path

import numpy as np
import numpy.testing

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

fillspill_dir = Path(__file__).parent.resolve() / "fillspill"


class FillSpillModel(ReservoirModel):
    """Class for simulating a pass flow model."""

    def apply_schemes(self):
        """Always apply pass flow."""
        self.apply_fillspill()


def test_fillspill():
    """Test the fillspill model."""
    config = ModelConfig(base_dir=fillspill_dir)
    model = FillSpillModel(config)
    model.simulate()
    output = model.extract_results()
    q_turbine = np.array(output["Q_turbine"])
    q_spill = np.array(output["Q_spill"])
    q_turbine_ref = np.array([0.0, 20, 20, 60, 60, 60, 60])
    q_spill_ref = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 63.0582, 50.9090])
    numpy.testing.assert_array_almost_equal(q_turbine, q_turbine_ref, decimal=3)
    numpy.testing.assert_array_almost_equal(q_spill, q_spill_ref, decimal=3)
