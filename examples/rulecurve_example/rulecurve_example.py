"""Example that illustrates use of the rulecurve scheme."""
from pathlib import Path

from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)
        self.calculate_rule_curve_deviation(periods=3, h_var="H_observed")
        self.adjust_rulecurve(
            periods=3,
            extrapolate_trend_linear=False,
        )

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        self.apply_rulecurve()


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(SingleReservoir, config=CONFIG)
