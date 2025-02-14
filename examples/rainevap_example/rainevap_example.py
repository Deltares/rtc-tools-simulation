"""Example that illustrates how to create a basic model."""

from pathlib import Path

from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        # Apply schemes.
        self.include_rainevap()
        self.set_q(
            target_variable="Q_turbine",
            input_type="parameter",
            input_data=1,
        )
        self.set_q(
            target_variable="Q_sluice",
            input_type="parameter",
            input_data="Q_sluice_target",
        )


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(SingleReservoir, config=CONFIG)
