"""Module for testing the qmin scheme."""
from pathlib import Path

import numpy as np
import numpy.testing
import pytest

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "minq"


class TestModel(ReservoirModel):
    """Class for testing the minq scheme."""

    def __init__(self, config: ModelConfig, h_target):
        super().__init__(config=config)
        self.h_target = h_target

    def apply_schemes(self):
        """Always apply spillway."""
        self.apply_minq(h_min=1.0, h_max=3.0, h_target=self.h_target)


@pytest.mark.parametrize(
    "h_target, h_ref",
    [
        (2.0, [2.0, 1.5, 3.0, 2.5]),
        ([2.0, 2.0, 2.0, 2.7], [2.0, 1.5, 3.0, 2.7]),
        ("H_target", [2.0, 1.5, 3.0, 2.7]),
    ],
)
def test_minq(h_target, h_ref):
    """Test the spillway model."""
    config = ModelConfig(base_dir=BASE_DIR)
    model = TestModel(config, h_target=h_target)
    model.simulate()
    output = model.extract_results()
    h_model = np.array(output["H"])
    numpy.testing.assert_array_almost_equal(h_model, h_ref, decimal=3)
