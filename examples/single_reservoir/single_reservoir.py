"""Example that illustrates how to create a basic model."""
from pathlib import Path

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        # Get current time.
        datetime = self.get_current_datetime()
        # Apply schemes.
        h = self.get_var("H")
        h_crest = self.get_var("H_crest")
        self.include_rainevap()
        if h > h_crest:
            april = 4
            september = 9
            if april <= datetime.month <= september:
                self.set_q(
                    target_variable="Q_out",
                    input_type="parameter",
                    input_data=0.2,
                )
            else:
                self.apply_spillway()
        else:
            self.set_q(
                target_variable="Q_out",
                input_type="parameter",
                input_data=0.4,
            )

    def calculate_output_variables(self):
        """Calculate additional output variables."""
        self.calculate_rule_curve_deviation(periods=3)


# Create and run the model.
if __name__ == "__main__":
    model = SingleReservoir(CONFIG)
    model.simulate()
