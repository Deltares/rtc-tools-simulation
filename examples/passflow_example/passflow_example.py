"""Example that illustrates use of the passflow scheme."""

from pathlib import Path

from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import InputVar, ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        # Get current time.
        datetime = self.get_current_datetime()
        # Apply schemes.
        day_12 = 12
        day_19 = 19
        if day_12 <= datetime.day <= day_19:
            self.apply_passflow()
        else:
            self.set_q(
                target_variable=InputVar.Q_OUT,
                input_type="timeseries",
                input_data="Q_out_target",
                apply_func="INST",
            )


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(SingleReservoir, config=CONFIG)
