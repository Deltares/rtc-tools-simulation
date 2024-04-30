"""Module for testing the passflow scheme."""
from pathlib import Path

import numpy as np
import numpy.testing
from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"
OUTPUT_DIR = BASE_DIR / "output_passflow"


class PassFlowModel(ReservoirModel):
    """Class for simulating a pass flow model."""

    def apply_schemes(self):
        """Always apply pass flow."""
        self.apply_passflow()


def test_passflow():
    """Test the passflow model."""
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})
    model = PassFlowModel(config)
    model.simulate()
    output = model.extract_results()
    q_out = np.array(output["Q_out"])
    v_out = np.array(output["V"])
    q_ref = np.array([0.0, 0.0, 1.0])
    v_ref = np.array([1.3, 1.3, 1.3])
    numpy.testing.assert_array_almost_equal(q_out, q_ref, decimal=3)
    numpy.testing.assert_array_almost_equal(v_out, v_ref, decimal=3)
