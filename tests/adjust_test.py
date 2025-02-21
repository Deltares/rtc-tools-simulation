"""Module for testing the adjust model"""
from pathlib import Path

import numpy.testing

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

adjust_dir = Path(__file__).parent.resolve() / "adjust"


class AdjustModel(ReservoirModel):
    """Class for simulating a model with an adjust scheme."""

    def apply_schemes(self):
        """Always adjust volume V to equal V_observed.
        Close the waterbalance through Q_error and Q_out_corrected"""
        if self.get_current_time() > self.get_start_time():
            self.set_var("Q_turbine", 3)
            self.apply_adjust()


def test_adjust():
    """Test the adjust model.
    Test for both volume and Q error to be correct"""
    config = ModelConfig(base_dir=adjust_dir)
    model = AdjustModel(config)
    model.simulate()
    final_h = model.get_var("H")
    final_qout = model.get_var("Q_out")
    final_qout_corr = model.get_var("Q_out_corrected")
    final_qerror = model.get_var("Q_error")
    test_outcome = [final_h, final_qout, final_qerror, final_qout_corr]
    expected = [1542.306754, 3.0, -0.808, 3.808]
    numpy.testing.assert_array_almost_equal(test_outcome, expected, decimal=3)
