"""Module for a reservoir model."""
import logging
import math
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
        self.max_reservoir_area = 0  # Set during pre().

    # Methods for preprocsesing.
    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)
        # Set default input timeseries.
        ref_series = self.io.get_timeseries("Q_in")
        times = ref_series[0]
        zeros = np.full(len(times), 0.0)
        timeseries = self.io.get_timeseries_names()
        optional_timeseries = ["V_observed", "mm_evaporation_per_hour", "mm_rain_per_hour"]
        for var in optional_timeseries:
            if var not in timeseries:
                self.io.set_timeseries(var, times, zeros)
                logger.info(f"{var} not found in the input file. Setting it to 0.0.")
        # Set parameters.
        self.max_reservoir_area = self.parameters().get("max_reservoir_area", 0)

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

    def apply_adjust(self):
        """
        Activate functionality to adjust water balance based on observed volume
        The function will close the water balance through the use of Q_error, which
        will cover the difference between the simulated Q_out and the observed volume change.
        """
        t = self.get_current_time()
        v_observed = self.timeseries_at("V_observed", t)
        self.set_var("V_observed", v_observed)  ## Load v_observed for this timestep
        self.set_var("compute_v", False)  ## Disable compute_v so V will equal v_observed

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
        if np.isnan(self.get_var("V_observed")):
            self.set_var("V_observed", 0)
        self.set_var("do_spill", False)
        self.set_var("do_pass", False)
        self.set_var("do_poolq", False)
        self.set_var("include_rain", False)
        self.set_var("include_evaporation", False)
        self.set_var("compute_v", True)

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
        input_data: str = None,
        apply_func: str = "MEAN",
        timestep: int = None,
        nan_option: str = None,
    ):
        """
        Set one of the input or output discharges to a given value,
        or a value determined from an input list.

        :param target_variable: str (default: 'Q_turbine')
            The variable that is to be set. Needs to be an internal variable, limited to discharges
        :param input_type: str (default: 'timeseries')
            The type of target data. Either 'timeseries' or 'parameter'. If it is a timeseries,
            the timeseries is assumed to have a regular time interval.
        :param input_data: str (default: None)
            the name of the target data. If not provided, it is set to the name of
            the target_variable. Name of timeseries_ID/parameter_ID in .xml file
        :param apply_func: str (default: 'MEAN')
            Function that is used to find the fixed_value if input_type = 'timeseries'.
            'MEAN' (default): Finds the average value, excluding nan-values.
            'MIN': Finds the minimum value, excluding nan-values.
            'MAX': Finds the maximum value, excluding nan-values.
            'INST': Finds the value marked by the corresponding timestep 't'. If the
            selected value is NaN, nan_option determines the
            procedure to find a valid value.
        :param timestep: int (default: None)
            The timestep at which the input data should be read at if input_type = 'timeseries',
            the default is the current timestep of the simulation run.
        :param nan_option:  str (default: None)
            the user can indicate the action to be take if missing values are found.
            Usable in combination with input_type = 'timeseries' and apply_func = 'INST'.
            'MEAN': It will take the mean of the timeseries excluding nans.
            'PREV': It attempts to find the closest previous valid data point.
            'NEXT':  It attempts to find the closest next valid data point.
            'CLOSEST': It attempts to find the closest valid data point,
            either backwards or forward. If same distance, take average.
            'INTERP': Interpolates linearly between the closest forward and backward data points.

        :return: Updated model with adjusted Q_variable

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
