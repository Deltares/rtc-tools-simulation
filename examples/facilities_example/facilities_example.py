"""Example that illustrates use of facilities only."""

from pathlib import Path

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""
    def initialize(self, *args, **kwargs):
        super().initialize()
        print(self.facilities) ## Display facilities

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""



# Create and run the model.
if __name__ == "__main__":
    model = SingleReservoir(CONFIG)
    model.simulate()
