"""Example that illustrates use of the suminf and floodflag utilities."""

from pathlib import Path

import numpy as np
from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import InputVar, ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)
        # Find the cumulative inflows. This scheme will also set the "cumulative_inflow" timeseries
        self.calculate_cumulative_inflows()

        # Get the flood flag for this model run
        # Note: these parameters could also be provided via the rtcDataConfig.xml
        self.flood_elevation = 1598.7
        self.q_out_daily_average = 1.0
        flood_flag = self.get_flood_flag(
            q_out_daily_average=self.q_out_daily_average,
            flood_elevation=self.flood_elevation,
        )

        # Set the flood flag and flood elevation as timeseries such that they can be plotted.
        # Note: these timeseries are not used in the simulation, but only for plotting.
        flood_flag_ts = np.full_like(self.times(), flood_flag)
        self.set_timeseries("flood_flag", flood_flag_ts)
        flood_elevation_ts = np.full_like(self.times(), self.flood_elevation)
        self.set_timeseries("flood_elevation", flood_elevation_ts)

    def apply_schemes(self):
        """Apply the schemes."""
        # Set the outflow to the q_out_daily_average value.
        self.set_q(
            target_variable=InputVar.Q_OUT,
            input_type="parameter",
            input_data=self.q_out_daily_average,
        )


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(SingleReservoir, config=CONFIG)
