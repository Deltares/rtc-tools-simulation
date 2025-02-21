"""Module for testing the qmin scheme."""
from pathlib import Path

import numpy as np
import numpy.testing

from rtctools_simulation.reservoir.minq import QMinParameters
from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "minq"


class TestModel(ReservoirModel):
    """Class for testing the minq scheme."""

    def apply_schemes(self):
        """Always apply spillway."""
        params = QMinParameters(h_min=1.0, h_max=3.0, h_target=2.0)
        self.apply_minq(params=params)


def test_minq():
    """Test the spillway model."""
    config = ModelConfig(base_dir=BASE_DIR)
    model = TestModel(config)
    model.simulate()
    output = model.extract_results()
    v = np.array(output["V"])
    v_ref = np.array([2.0, 1.5, 3.0])
    numpy.testing.assert_array_almost_equal(v, v_ref, decimal=3)
