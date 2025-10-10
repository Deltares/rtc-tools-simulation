"""Module for testing the qmin scheme."""
from pathlib import Path

import numpy as np
import numpy.testing
import pytest

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "minq"


class TestModel(ReservoirModel):
    """Class for testing the minq scheme."""

    def __init__(self, config: ModelConfig, h_target, q_max):
        super().__init__(config=config)
        self.h_target = h_target
        self.q_max = q_max

    def apply_schemes(self):
        """Always apply spillway."""
        self.apply_minq(h_min=1.0, h_max=3.0, h_target=self.h_target, q_max=self.q_max)


@pytest.mark.parametrize(
    "h_target, q_max, h_ref, q_ref",
    [
        (2.0, np.inf, [2.0, 1.5, 3.0, 2.5], [0.0, 0.5, 0.5, 0.5]),
        ([2.0, 2.0, 2.0, 2.7], np.inf, [2.0, 1.5, 3.0, 2.699], [0.0, 0.5, 0.5, 0.301]),
        ("H_target", np.inf, [2.0, 1.5, 3.0, 2.699], [0.0, 0.5, 0.5, 0.301]),
        (2.0, 0.4, [2.0, 1.6, 3.2, 2.8], [0.0, 0.4, 0.4, 0.4]),
    ],
)
def test_minq(h_target, q_max, h_ref, q_ref):
    """Test the spillway model."""
    config = ModelConfig(base_dir=BASE_DIR)
    model = TestModel(config, h_target=h_target, q_max=q_max)
    model.simulate()
    output = model.extract_results()
    h_model = np.array(output["H"])
    q_model = np.array(output["Q_out"])
    numpy.testing.assert_array_almost_equal(h_model, h_ref, decimal=3)
    numpy.testing.assert_array_almost_equal(q_model, q_ref, decimal=3)
