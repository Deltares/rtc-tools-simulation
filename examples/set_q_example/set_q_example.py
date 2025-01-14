"""Example that illustrates use of set_q scheme only."""

from pathlib import Path

from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        # Collect reservoir elevation.
        h = self.get_var("H")
        critical_h = 1598.54
        if h > critical_h:
            self.set_q(
                target_variable="Q_out",
                input_type="parameter",
                input_data=0.4,
            )
        else:
            self.set_q(
                target_variable="Q_out",
                input_type="parameter",
                input_data=0.2,
            )


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(SingleReservoir, config=CONFIG)
