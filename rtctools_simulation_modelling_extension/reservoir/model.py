"""Module for a reservoir model."""
from datetime import datetime
from pathlib import Path

from rtctools_simulation_modelling_extension.model import Model, ModelConfig

MODEL_DIR = Path(__file__).parent.parent / "modelica" / "reservoir"


class ReservoirModel(Model):
    """Class for a reservoir model."""

    def __init__(self, config: ModelConfig, use_default_model=True, **kwargs):
        if use_default_model:
            config.set_dir("model", MODEL_DIR)
            config.set_model("Reservoir")
        super().__init__(config, **kwargs)

    # Helper functions for getting the time/date.
    def sec_to_datetime(self, time_in_seconds) -> datetime:
        """Convert time in seconds to datetime."""
        return self.io.sec_to_datetime(time_in_seconds, self.io.reference_datetime)

    def get_next_time(self) -> float:
        """Get the next time value (in seconds)."""
        return self.get_current_time() + self.get_time_step()

    def get_next_datetime(self) -> datetime:
        """Get the next time value (in datetime)."""
        return self.sec_to_datetime(self.get_next_time())

    # Schemes
    def set_q(self, value):
        """Set Q_turbine."""
        # TODO: this should be updated.
        self.set_var("Q_turbine", value)

    def apply_spillway(self, do_spill=True):
        """Enable water to spill from the reservoir."""
        self.set_var("do_spill", do_spill)

    def apply_passflow(self, do_pass=True):
        """Let the outflow be the same as the inflow."""
        if do_pass:
            self.set_var("do_poolq", False)
        self.set_var("do_pass", do_pass)

    def apply_poolq(self, do_poolq=True):
        """Let the outflow be determined by a lookup table."""
        if do_poolq:
            self.set_var("do_pass", False)
        self.set_var("do_poolq", do_poolq)

    # Methods for applying schemes / setting input.
    def set_default_input(self):
        """Set default input values."""
        time = self.get_current_time()
        q_turbine = self.timeseries_at("Q_turbine", time)
        self.set_var("Q_turbine", q_turbine)
        self.set_var("do_spill", False)
        self.set_var("do_pass", False)
        self.set_var("do_poolq", False)

    def apply_schemes(self):
        """
        Apply schemes.

        This method should be overwritten by the user.
        """
        pass

    def initialize_input_variables(self):
        """Initialize input variables."""
        self.set_default_input()

    def set_input_variables(self):
        """Set input variables."""
        self.set_default_input()
        self.apply_schemes()

    # Plotting
    def get_output_variables(self):
        variables = super().get_output_variables().copy()
        variables.extend(["Q_in"])
        variables.extend(["Q_turbine"])
        return variables
