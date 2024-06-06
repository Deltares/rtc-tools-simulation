"""Example that illustrates use of the adjust scheme."""

from pathlib import Path

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        # Apply schemes.
        self.set_q(
            target_variable="Q_out",
            input_type="parameter",
            input_data=0.4,
        )
        self.apply_adjust()


# Create and run the model.
if __name__ == "__main__":
    model = SingleReservoir(CONFIG)
    model.simulate()
