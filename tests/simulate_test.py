"""Module for testing the simulate module."""
import logging
from pathlib import Path

import numpy as np
import numpy.testing

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel
from rtctools_simulation.simulate import simulate

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"


class SpillwayModel(ReservoirModel):
    """Class for simulating a spillway model."""

    def apply_schemes(self):
        """Always apply spillway."""
        self.apply_spillway()


def test_simulate(log_level=logging.INFO):
    """Test the simulate function."""
    config = ModelConfig(base_dir=BASE_DIR)
    model = SpillwayModel(config)
    model: SpillwayModel = simulate(
        SpillwayModel, model_kwargs={"config": config}, log_level=log_level
    )
    output = model.extract_results()
    v = np.array(output["V"])
    v_ref = np.array([1.3, 0.8, 1.2])
    numpy.testing.assert_array_almost_equal(v, v_ref, decimal=3)


if __name__ == "__main__":
    test_simulate(log_level=logging.DEBUG)
