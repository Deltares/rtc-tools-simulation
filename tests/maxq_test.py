"""Module for testing the adjust model"""
from pathlib import Path

import numpy as np

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

maxq_dir = Path(__file__).parent.resolve() / "maxq"


class MaxQModel(ReservoirModel):
    """Class for simulating a model with an adjust scheme."""

    def pre(self, **kwargs):
        super().pre()
        self.maxq = np.zeros(shape=(3, 3))

    def apply_schemes(self):
        if self.get_current_time() > 0:
            maxq1 = self.find_maxq("Spillway")
            maxq2 = self.find_maxq("Fixed")
            maxq3 = self.find_maxq("Tailwater")
            print("Maxq1: ", maxq1)
            print("Maxq2: ", maxq2)
            print("Maxq3: ", maxq3)
            timestep_int = int(self.get_current_time() / self.get_time_step())
            self.maxq[timestep_int, 0] = maxq1
            self.maxq[timestep_int, 1] = maxq2
            self.maxq[timestep_int, 2] = maxq3
            print(self.maxq)


case1_outcome = np.array([0, 0.65, 1.4])

case2_outcome = np.array([0, 0.5, 0.5])

case3_outcome = np.array([0, 0.4833, 1.28])


def test_maxq():
    """Test the maxq utility. Test all 3 cases"""
    config = ModelConfig(base_dir=maxq_dir)
    model = MaxQModel(config)
    model.simulate()
    sim_maxq = model.maxq
    np.testing.assert_array_almost_equal(case1_outcome, sim_maxq[:, 0], decimal=3)
    np.testing.assert_array_almost_equal(case2_outcome, sim_maxq[:, 1], decimal=3)
    np.testing.assert_array_almost_equal(case3_outcome, sim_maxq[:, 2], decimal=3)
