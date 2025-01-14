"""Module for a reservoir model."""
import filecmp
import logging
import math
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

import casadi as ca
import numpy as np
import pandas as pd

import rtctools_simulation.lookup_table as lut
import rtctools_simulation.reservoir.setq_help_functions as setq_functions
from rtctools_simulation.model import Model, ModelConfig
from rtctools_simulation.reservoir.rule_curve import rule_curve_discharge
from rtctools_simulation.reservoir.rule_curve_deviation import (
    rule_curve_deviation,
)

DEFAULT_MODEL_DIR = Path(__file__).parent.parent / "modelica" / "reservoir"

logger = logging.getLogger("rtctools")

#: Reservoir model variables.
VARIABLES = [
    "Area",
    "H",
    "H_crest",
    "Q_evap",
    "Q_in",
    "Q_out",
    "Q_rain",
    "Q_spill",
    "Q_turbine",
    "Q_sluice",
    "V",
]


class ReservoirModel(Model):
    """Class for a reservoir model."""

    def __init__(self, config: ModelConfig, use_default_model=True, **kwargs):
        """
        Initialize the model.

        :param use_default_model BOOL: (default=True)
            If true, the default single reservoir model will be used.
        """
        if use_default_model:
            self._create_model(config)
        super().__init__(config, **kwargs)
        self.max_reservoir_area = 0  # Set during pre().

    def _get_lookup_tables(self) -> Dict[str, ca.Function]:
        lookup_tables = super()._get_lookup_tables()
        equations_csv = self._config.get_file("lookup_table_equations.csv", dirs=["model"])
        assert equations_csv.is_file()
        equations_df = pd.read_csv(equations_csv, sep=",")
        for _, equation_df in equations_df.iterrows():
            name = equation_df["lookup_table"]
            var_in: str = equation_df["var_in"]
            var_in = var_in.split(" ")
            var_in = [var for var in var_in if var != ""]
            if name not in lookup_tables:
                warning = f"Lookup table {name} not found. Using an empty lookup table instead."
                logger.warning(warning)
                var_out = equation_df["var_out"]
                lookup_table = lut.get_empty_lookup_table(name, var_in, var_out)
                lookup_tables[name] = lookup_table
        return lookup_tables

    def _create_model(self, config: ModelConfig):
        """Create a model folder based on the default model."""
        base_dir = config.base_dir()
        if base_dir is None:
            raise ValueError("A base directory should be set when using the default model.")
        model_dir = base_dir / "generated_model"
        if not model_dir.is_dir():
            model_dir.mkdir()
        config.set_dir("model", model_dir)
        config.set_model("Reservoir")
        for filename in ["reservoir.mo", "lookup_table_equations.csv"]:
            default_file = DEFAULT_MODEL_DIR / filename
            file = model_dir / filename
            if file.is_file() and filecmp.cmp(default_file, file, shallow=False):
                continue
            shutil.copy2(default_file, file)

    # Methods for preprocsesing.
    def pre(self, *args, **kwargs):
        """
        This method can be overwritten to perform any pre-processing before the simulation begins.

        .. note:: Be careful if you choose to overwrite this method as default values have been
            carefully chosen to select the correct default schemes.
        """
        super().pre(*args, **kwargs)
        # Set default input timeseries.
        ref_series = self.io.get_timeseries("Q_in")
        times = ref_series[0]
        zeros = np.full(len(times), 0.0)
        timeseries = self.io.get_timeseries_names()
        optional_timeseries = [
            "H_observed",
            "mm_evaporation_per_hour",
            "mm_rain_per_hour",
            "Q_turbine",
            "Q_sluice",
            "Q_out_from_input",
        ]
        # to prevent infeasibilities this value needs to be within the range of the lookup table
        # We use the intial volume or elevation to ensure this.
        if "V" in timeseries:
            self.default_h = float(self._lookup_tables["h_from_v"](self.get_timeseries("V")[0]))
        elif "H" in timeseries:
            self.default_h = float(self.get_timeseries("H")[0])
        elif "H_observed" in timeseries:
            self.default_h = float(self.get_timeseries("H_observed")[0])
        else:
            raise Exception(
                'No initial condition is provided for reservoir elevation, "H", '
                'reservoir volume, "V", or observed elevation "H_observed". '
                "One of these must be provided."
            )
        for var in optional_timeseries:
            if var not in timeseries:
                if var == "H_observed":
                    self.io.set_timeseries(var, times, [self.default_h] * len(times))
                    logger.info(
                        f"{var} not found in the input file. Setting it to {self.default_h}."
                    )
                else:
                    self.io.set_timeseries(var, times, zeros)
                    logger.info(f"{var} not found in the input file. Setting it to 0.0.")
            if np.any(np.isnan(self.get_timeseries(var))):
                if var == "H_observed":
                    self.io.set_timeseries(
                        var,
                        times,
                        [self.default_h if np.isnan(x) else x for x in self.get_timeseries(var)],
                    )
                    logger.info(
                        f"{var} contains NaNs in the input file. "
                        f"Setting these values to {self.default_h}."
                    )
                else:
                    self.io.set_timeseries(
                        var, times, [0 if np.isnan(x) else x for x in self.get_timeseries(var)]
                    )
                    logger.info(
                        f"{var} contains NaNs in the input file. Setting these values to 0.0."
                    )
        # Set parameters.
        self.max_reservoir_area = self.parameters().get("max_reservoir_area", 0)

    # Helper functions for getting the time/date/variables.
    def get_var(self, var: str) -> float:
        """
        Get the value of a given variable at the current time.

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

    def get_current_time(self) -> int:
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

    def set_time_step(self, dt):
        """
        Set the time step size.

        :meta private:
        """
        # TODO: remove once set_q allows variable dt.
        current_dt = self.get_time_step()
        if current_dt is not None and not math.isclose(dt, current_dt):
            raise ValueError("Timestep size cannot change during simulation.")
        super().set_time_step(dt)

    # Schemes
    def apply_spillway(self):
        """Scheme to enable water to spill from the reservoir.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        This scheme ensures that the spill "Q_spill" is computed from the elevation "H" using a
        lookuptable "qspill_from_h".
        """
        self.set_var("do_spill", True)

    def apply_adjust(self):
        """Scheme to adjust simulated volume to observed volume.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        Observed pool elevations (H_observed) can be provided to the model, internally these are
        converted to observed volumes (V_observed) via the lookup table ``h_from_v''.
        When applying this scheme, V is set to V_observed and a corrected version of the outflow,
        Q_out_corrected, is calculated in order to preserve the mass balance.
        """
        t = self.get_current_time()
        h_observed = self.timeseries_at("H_observed", t)
        empty_observation = self.default_h
        if h_observed == empty_observation:
            logger.debug("there are no observed elevations at time {t}")
        else:
            self.set_var("compute_v", False)  ## Disable compute_v so V will equal v_observed

    def apply_passflow(self):
        """Scheme to let the outflow be the same as the inflow.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.

        .. note:: This scheme cannot be used in combination with
            :py:meth:`.ReservoirModel.apply_poolq`, or :py:meth:`.ReservoirModel.set_q` when the
            target variable is Q_out.
        """
        self.set_var("do_poolq", False)
        self.set_var("do_pass", True)
        self.set_var("do_set_q_out", False)

    def apply_poolq(self):
        """Scheme to let the outflow be determined by a lookup table with name "qout_from_v".

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.

        It is possible to impose a dependence on days using the “qout_from_v” lookup table
        If this is not needed then the “day” column should be constant (e.g. = 1)
        Otherwise a 2D lookup table is created by linear interpolation between days, Q_out and V.

        .. note:: This scheme cannot be used in combination with
            :py:meth:`.ReservoirModel.apply_passflow`, or :py:meth:`.ReservoirModel.set_q` when the
            target variable is Q_out.
        """
        self.set_var("do_pass", False)
        self.set_var("do_poolq", True)
        self.set_var("do_set_q_out", False)

    def include_rain(self):
        """Scheme to  include the effect of rainfall on the reservoir volume.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        This scheme computes

             Q_rain = max_reservoir_area * mm_rain_per_hour / 3600 / 1000 * include_rain.

        This is then treated in the mass balance of the reservoir

            der(V) = Q_in - Q_out + Q_rain - Q_evap.

        .. note:: To include rainfall, make sure to set the max_reservoir_area parameter.
        """
        assert (
            self.max_reservoir_area > 0
        ), "To include rainfall, make sure to set the max_reservoir_area parameter."
        self.set_var("include_rain", True)

    def include_evaporation(self):
        """Scheme to include the effect of evaporation on the reservoir volume.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        This scheme computes

            Q_evap = Area * mm_evaporation_per_hour / 3600 / 1000 * include_evaporation.

        This is then treated in the mass balance of the reservoir

            der(V) = Q_in - Q_out + Q_rain - Q_evap.
        """
        self.set_var("include_evaporation", True)

    def include_rainevap(self):
        """Scheme to include the effect of both rainfall and evaporation on the reservoir volume.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        This scheme implements both :py:meth:`.ReservoirModel.include_rain`
        and :py:meth:`.ReservoirModel.include_evaporation`.
        """
        self.include_evaporation()
        self.include_rain()

    def apply_rulecurve(self, outflow: str = "Q_turbine"):
        """Scheme to set the outflow of the reservoir in order to reach a rulecurve.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        This scheme uses the lookup table ``v_from_h`` and requires the following parameters
        from the ``rtcParameterConfig.xml`` file.

            - ``rule_curve_q_max``: Upper limiting discharge while blending pool elevation
              (m^3/timestep)
            - ``rule_curve_blend``:  Number of timesteps over which to bring the pool back to the
              scheduled elevation.

        The user must also provide a timeseries with the name ``rule_curve``. This contains the
        water level target for each timestep.

        :param outflow: outflow variable that is modified to reach the rulecurve.

        .. note:: This scheme does not correct for the inflows to the reservoir. As a result,
            the resulting height may differ from the rule curve target.
        """
        current_step = int(self.get_current_time() / self.get_time_step())
        q_max = self.parameters().get("rule_curve_q_max")
        if q_max is None:
            raise ValueError(
                "The parameter rule_curve_q_max is not set, "
                + "which is required for the rule curve scheme"
            )
        blend = self.parameters().get("rule_curve_blend")
        if blend is None:
            raise ValueError(
                "The parameter rule_curve_blend is not set, "
                "which is required for the rule curve scheme"
            )
        try:
            rule_curve = self.io.get_timeseries("rule_curve")[1]
        except KeyError as exc:
            raise KeyError("The rule curve timeseries is not found in the input file.") from exc
        v_from_h_lookup_table = self.lookup_tables().get("v_from_h")
        if v_from_h_lookup_table is None:
            raise ValueError(
                "The lookup table v_from_h is not found"
                " It is required for the rule curve scheme."
            )
        volume_target = v_from_h_lookup_table(rule_curve[current_step])
        current_volume = self.get_var("V")
        discharge = rule_curve_discharge(
            volume_target,
            current_volume,
            q_max,
            blend,
        )
        discharge_per_second = discharge / self.get_time_step()
        self.set_var(outflow, discharge_per_second)
        logger.debug(
            "Rule curve function has set the " + f"{outflow} to {discharge_per_second} m^3/s"
        )

    def calculate_rule_curve_deviation(
        self,
        periods: int,
        inflows: Optional[np.ndarray] = None,
        q_max: float = np.inf,
        maximum_difference: float = np.inf,
    ):
        """Calculate the moving average between the rule curve and the simulated elevations.

        This method can be applied inside :py:meth:`.ReservoirModel.calculate_output_variables`.

        This method calculates the moving average between the rule curve and the simulated
        elevations over a specified number of periods. It takes the following parameters:

        :param periods: The number of periods over which to calculate the moving average.
        :param inflows: Optional. The inflows to the reservoir. If provided, the moving average
                        will be calculated only for the periods with non-zero inflows.
        :param q_max: Optional. The maximum discharge allowed while calculating the moving average.
                      Default is infinity, required if q_max is set.
        :param maximum_difference: Optional. The maximum allowable difference between the rule curve
                                   and the simulated elevations.

        .. note:: The rule curve timeseries must be present in the timeseries import. The results
            are stored in the timeseries "rule_curve_deviation".
        """
        observed_elevations = self.extract_results().get("H")
        try:
            rule_curve = self.io.get_timeseries("rule_curve")[1]
        except KeyError as exc:
            raise KeyError("The rule curve timeseries is not found in the input file.") from exc
        deviations = rule_curve_deviation(
            observed_elevations,
            rule_curve,
            periods,
            inflows=inflows,
            q_max=q_max,
            maximimum_difference=maximum_difference,
        )
        self.set_timeseries("rule_curve_deviation", deviations)
        self.extract_results().update({"rule_curve_deviation": deviations})

    # Methods for applying schemes / setting input.
    def set_default_input(self):
        """Set default input values.

        This method sets default values for internal variables at each timestep.
        This is important to ensure that the schemes behave as expected.
        """
        if np.isnan(self.get_var("Q_turbine")):
            self.set_var("Q_turbine", 0)
        if np.isnan(self.get_var("Q_sluice")):
            self.set_var("Q_sluice", 0)
        if np.isnan(self.get_var("H_observed")):
            self.set_var("H_observed", self.default_h)
        if np.isnan(self.get_var("Q_out_from_input")):
            self.set_var("Q_out_from_input", 0)
        self.set_var("do_spill", False)
        self.set_var("do_pass", False)
        self.set_var("do_poolq", False)
        self.set_var("include_rain", False)
        self.set_var("include_evaporation", False)
        self.set_var("compute_v", True)
        self.set_var("do_set_q_out", False)
        day = self.get_current_datetime().day
        self.set_var("day", day)

    def apply_schemes(self):
        """
        Apply schemes.

        This method is called at each timestep and should be implemented by the user.
        This method should contain the logic for which scheme is applied under which conditions.
        """
        pass

    def calculate_output_variables(self):
        """
        Calculate output variables.

        This method is called after the simulation has finished.
        The user can implement this method to calculate additional output variables.
        """
        pass

    def set_input_variables(self):
        """Set input variables.

        This method calls :py:meth:`.ReservoirModel.set_default_input` and
        :py:meth:`.ReservoirModel.apply_schemes`.
        This method can be overwritten to set input at each timestep.

        .. note:: Be careful if you choose to overwrite this method as default values have been
            carefully chosen to select the correct default schemes.
        """
        self.set_default_input()
        self.apply_schemes()

    # Plotting
    def get_output_variables(self):
        """Method to get, and extend output variables

        This method gets all output variables of the reservoir model, and extends the
        output to also include input variables like "Q_in" and "Q_turbine" such that they appear in
        the timeseries_export.xml.
        """
        variables = super().get_output_variables().copy()
        variables.extend(["Q_in"])
        variables.extend(["Q_turbine"])
        variables.extend(["Q_sluice"])
        return variables

    def set_q(
        self,
        target_variable: str = "Q_turbine",
        input_type: str = "timeseries",
        input_data: Union[str, float, list[float]] = None,
        apply_func: str = "MEAN",
        timestep: int = None,
        nan_option: str = None,
    ):
        """
        Scheme to set one of the input or output discharges to a given value,
        or a value determined from an input list.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.

        .. note:: This scheme cannot be used
            in combination with :py:meth:`.ReservoirModel.apply_poolq`, or
            :py:meth:`.ReservoirModel.apply_passflow` if the target variable is Q_out.

        :param target_variable: str (default: 'Q_turbine')
            The variable that is to be set. Needs to be an internal variable, limited to discharges.
        :param input_type: str (default: 'timeseries')
            The type of target data. Either 'timeseries' or 'parameter'. If it is a timeseries,
            the timeseries is assumed to have a regular time interval.
        :param input_data: str | float | list[float] (default: None)
            Single value or a list of values for each time step to set the target.
            It can also be a name of a parameter or input variable.
        :param apply_func: str (default: 'MEAN')
            Function that is used to find the fixed_value if input_type = 'timeseries'.

                - 'MEAN' (default): Finds the average value, excluding nan-values.
                - 'MIN': Finds the minimum value, excluding nan-values.
                - 'MAX': Finds the maximum value, excluding nan-values.
                - 'INST': Finds the value marked by the corresponding timestep 't'. If the
                  selected value is NaN, nan_option determines the procedure to find a valid
                  value.

        :param timestep: int (default: None)
            The timestep at which the input data should be read at if input_type = 'timeseries',
            the default is the current timestep of the simulation run.
        :param nan_option: str (default: None)
            the user can indicate the action to be take if missing values are found.
            Usable in combination with input_type = 'timeseries' and apply_func = 'INST'.

                - 'MEAN': It will take the mean of the timeseries excluding nans.
                - 'PREV': It attempts to find the closest previous valid data point.
                - 'NEXT': It attempts to find the closest next valid data point.
                - 'CLOSEST': It attempts to find the closest valid data point, either backwards or
                  forward. If same distance, take average.
                - 'INTERP': Interpolates linearly between the closest forward and backward data
                  points.
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
