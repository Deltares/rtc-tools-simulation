"""Example that illustrates use of the rulecurve scheme."""
import datetime
from pathlib import Path

from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import InputVar, ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)
        self.calculate_rule_curve_deviation(periods=3)
        self.adjust_rulecurve(
            periods=3,
            extrapolate_trend_linear=False,
            application_time=datetime.datetime(2022, 6, 13, 0),
        )

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        self.apply_rulecurve(outflow=InputVar.Q_TURBINE)


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(SingleReservoir, config=CONFIG)
