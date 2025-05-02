"""Example that illustrates use of the maxq utility."""
from pathlib import Path

import numpy as np
from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class MaxQModel(ReservoirModel):
    """Class for simulating a model with an adjust scheme."""

    #
    # def __init__(self, **kwargs):
    #     super().__init__(use_default_model= False, config= CONFIG)
    #

    def pre(self, **kwargs):
        super().pre()
        self.maxq = np.zeros(shape=(3, 3))

    def apply_schemes(self):
        print(self.get_current_time())
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

    def calculate_output_variables(self):  # Tool to plot the maximum discharges
        # TODO Add results to plot
        results = self.extract_results()
        results["Qmax_spillway"] = self.maxq[:, 0]
        results["Qmax_fixed"] = self.maxq[:, 1]
        results["Qmax_tailwater"] = self.maxq[:, 2]
        return results


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(MaxQModel, config=CONFIG)
