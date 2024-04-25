"""Module for a reservoir model."""
import logging
import math
import logging
from datetime import datetime
from pathlib import Path

import numpy as np

import rtctools_simulation_modelling_extension.reservoir.setq_help_functions as setq_functions
from rtctools_simulation_modelling_extension.model import Model, ModelConfig

MODEL_DIR = Path(__file__).parent.parent / "modelica" / "reservoir"

logger = logging.getLogger("rtctools")

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

    def get_current_time(self):
        """
        Get the current time (in seconds).

        :returns: the current time (in seconds).
        """
        return super().get_current_time()

    def get_current_datetime(self) -> datetime:
        """
        Get the current datetime.

        :returns: the current time in datetime format.
        """
        current_time = self.get_current_time()
        return self.io.sec_to_datetime(current_time, self.io.reference_datetime)

    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)

        # Set default inputs for rain and evaporation
        ref_series = self.io.get_timeseries("Q_in")
        self.max_reservoir_area = self.parameters().get("max_reservoir_area", 0)
        if "mm_evaporation_per_hour" not in list(self.io.get_timeseries_names()):
            self.io.set_timeseries(
                "mm_evaporation_per_hour", ref_series[0], np.full(len(ref_series[1]), 0.0)
            )
            logger.info("mm_evaporation_per_hour not found in the input file. Setting it to 0.0.")
        if "mm_rain_per_hour" not in list(self.io.get_timeseries_names()):
            self.io.set_timeseries(
                "mm_rain_per_hour", ref_series[0], np.full(len(ref_series[1]), 0.0)
            )
            logger.info("mm_rain_per_hour not found in the input file. Setting it to 0.0.")

    # Helper functions for getting the time/date.
    def sec_to_datetime(self, time_in_seconds) -> datetime:
        """Convert time in seconds to datetime."""
        return self.io.sec_to_datetime(time_in_seconds, self.io.reference_datetime)

    def set_time_step(self, dt):
        # TODO: remove once set_q allows variable dt.
        current_dt = self.get_time_step()
        if current_dt is not None and not math.isclose(dt, current_dt):
            raise ValueError("Timestep size cannot change during simulation.")
        super().set_time_step(dt)

    # Schemes
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

    def include_rain(self):
        """Include the effect of rainfall on the reservoir volume."""
        assert (
            self.max_reservoir_area > 0
        ), "To include rainfall, make sure to set the max_reservoir_area parameter."
        self.set_var("include_rain", True)

    def include_evaporation(self):
        """Include the effect of evaporation on the reservoir volume."""
        self.set_var("include_evaporation", True)

    def include_rainevap(self):
        """Include the effect of both rainfall and evaporation on the reservoir volume."""
        self.include_evaporation()
        self.include_rain()

    # Methods for applying schemes / setting input.
    def set_default_input(self):
        """Set default input values."""
        if np.isnan(self.get_var("Q_turbine")):
            self.set_var("Q_turbine", 0)
        self.set_var("do_spill", False)
        self.set_var("do_pass", False)
        self.set_var("do_poolq", False)
        self.set_var("include_rain", False)
        self.set_var("include_evaporation", False)

    def apply_schemes(self):
        """
        Apply schemes.

        This method is called at each timestep
        and should be implemented by the user.
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

    def set_q(
        self,
        target_variable: str = "Q_turbine",
        input_type: str = "timeseries",
        apply_func: str = "MEAN",
        input_data: str = None,
        timestep: int = None,
        nan_option: str = None,
    ):
        """
        Set a discharge input or output to a given value, or a value to be
        deduced from a given timeseries.
        """
        # TODO: enable set_q to handle variable timestep sizes.
        setq_functions.setq(
            self,
            target_variable,
            input_type,
            apply_func,
            input_data,
            timestep,
            nan_option,
        )
