"""Example that illustrates use of the rulecurve scheme."""

from pathlib import Path

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        self.apply_rulecurve(outflow="Q_sluice")


# Create and run the model.
if __name__ == "__main__":
    model = SingleReservoir(CONFIG)
    model.simulate()
