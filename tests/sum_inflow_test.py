"""Module for testing the functions for summing inflows."""

from pathlib import Path

import numpy as np
from numpy.testing import assert_array_almost_equal

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

adjust_dir = Path(__file__).parent.resolve() / "adjust"


class InflowFunctionModel(ReservoirModel):
    """Class for simulating a model with an inflow calculations."""

    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)
        self.calculate_cumulative_inflows()

    def apply_schemes(self):
        self.calculate_single_cumulative_inflow()


def test_cumulative_inflows():
    """Test the adjust model. Test for both volume to be correct"""
    config = ModelConfig(base_dir=adjust_dir)
    model = InflowFunctionModel(config)
    model.simulate()
    cum_in_ref = np.array([1, 2, 3, 3])
    assert_array_almost_equal(model.get_timeseries("cumulative_inflows"), cum_in_ref)
