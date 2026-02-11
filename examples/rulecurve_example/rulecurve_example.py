"""Example that illustrates use of the rulecurve scheme.

This example shows two variants:
- SingleReservoir: basic rule curve control
- SingleReservoirWithQmin: rule curve with minimum discharge enforcement

To switch between them, change the class passed to run_simulation_problem.
"""
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


class SingleReservoirWithQmin(SingleReservoir):
    """Example reservoir with minimum discharge enforcement.

    Extends SingleReservoir by enforcing a minimum outflow as
    configured by Reservoir_Qmin. When the reservoir level drops
    toward dead storage (Reservoir_Hdead, with buffer Reservoir_Hbuffer),
    the effective Qmin is linearly reduced to prevent over-release.

    Requires parameters Reservoir_Qmin, Reservoir_Hdead,
    and Reservoir_Hbuffer in rtcParameterConfig.xml.
    """

    def apply_schemes(self):
        """Apply rule curve with Qmin enforcement."""
        self.apply_rulecurve(enforce_qmin=True)


# Create and run the model.
# Change to SingleReservoir to disable Qmin enforcement.
if __name__ == "__main__":
    run_simulation_problem(SingleReservoirWithQmin, config=CONFIG)
