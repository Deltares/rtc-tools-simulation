"""Module for a reservoir model."""
from datetime import datetime
from pathlib import Path

from rtctools_simulation_modelling_extension.model import Model, ModelConfig

MODEL_DIR = Path(__file__).parent.parent / "modelica" / "reservoir"

#: Reservoir model variables.
VARIABLES = [
    "Area",
    "H",
    "H_crest",
    "Q_in",
    "Q_out",
    "Q_spill",
    "Q_turbine",
    "V",
]


class ReservoirModel(Model):
    """Class for a reservoir model."""

    def __init__(self, config: ModelConfig, use_default_model=True, **kwargs):
        if use_default_model:
            config.set_dir("model", MODEL_DIR)
            config.set_model("Reservoir")
        super().__init__(config, **kwargs)

    # Helper functions for getting the time/date/variables.
    def get_var(self, var: str):
        """
        Get the value of a given variable.

        :param var: name of the variable.
            Should be one of :py:const:`VARIABLES`.
        :returns: value of the given variable.
        """
        try:
            value = super().get_var(var)
        except KeyError:
            message = f"Variable {var} not found." f" Expected var to be one of {VARIABLES}."
            return KeyError(message)
        return value

    def get_current_datetime(self) -> datetime:
        """Get the current datetime."""
        current_time = self.get_current_time()
        return self.io.sec_to_datetime(current_time, self.io.reference_datetime)

    def sec_to_datetime(self, time_in_seconds) -> datetime:
        """Convert time in seconds to datetime."""
        return self.io.sec_to_datetime(time_in_seconds, self.io.reference_datetime)

    # Schemes
    def set_q(self, value):
        """Set Q_turbine."""
        # TODO: this should be updated.
        self.set_var("Q_turbine", value)

    def apply_spillway(self):
        """Enable water to spill from the reservoir."""
        self.set_var("do_spill", True)

    def apply_passflow(self):
        """Let the outflow be the same as the inflow."""
        self.set_var("do_poolq", False)
        self.set_var("do_pass", True)

    def apply_poolq(self):
        """Let the outflow be determined by a lookup table."""
        self.set_var("do_pass", False)
        self.set_var("do_poolq", True)

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
