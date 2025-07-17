"""Example that illustrates use of the maxq utility."""
from pathlib import Path

import numpy as np
from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class MaxQModel(ReservoirModel):
    """Class for simulating a model with an adjust scheme."""

    def pre(self, **kwargs):
        super().pre()
        self.maxq = np.zeros(shape=(3, 4))

    def apply_schemes(self):
        if self.get_current_time() > 0:
            maxq1 = self.find_maxq("Spillway")
            maxq2 = self.find_maxq("Fixed")
            maxq3 = self.find_maxq("Tailwater")
            maxq4 = self.find_maxq("Elevation_Qmax_LUT")
            timestep_int = int(self.get_current_time() / self.get_time_step())
            # Save the calculated maximum discharges to set as timeseries in postprocessing.
            self.maxq[timestep_int, 0] = maxq1
            self.maxq[timestep_int, 1] = maxq2
            self.maxq[timestep_int, 2] = maxq3
            self.maxq[timestep_int, 3] = maxq4

    def calculate_output_variables(self):
        # Set the calculated maximum discharges as timeseries such that they can be plotted.
        self.set_timeseries("Qmax_spillway", self.maxq[:, 0])
        self.set_timeseries("Qmax_fixed", self.maxq[:, 1])
        self.set_timeseries("Qmax_tailwater", self.maxq[:, 2])
        self.set_timeseries("Qmax_elevation", self.maxq[:, 3])


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(MaxQModel, config=CONFIG)
