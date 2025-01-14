"""Module for testing the poolq scheme."""
from pathlib import Path

import numpy as np
import numpy.testing

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"
OUTPUT_DIR = BASE_DIR / "output_poolq"


class PoolQModel(ReservoirModel):
    """Class for simulating a poolq model."""

    def apply_schemes(self):
        """Always apply poolq."""
        self.apply_poolq()


def test_poolq():
    """Test the poolq model."""
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})
    model = PoolQModel(config)
    model.simulate()
    output = model.extract_results()
    q_out = np.array(output["Q_out"])
    v_out = np.array(output["V"])
    q_ref = np.array([0.3, 0.15, 0.575])
    v_ref = np.array([1.3, 1.15, 1.575])
    numpy.testing.assert_array_almost_equal(q_out, q_ref, decimal=3)
    numpy.testing.assert_array_almost_equal(v_out, v_ref, decimal=3)
