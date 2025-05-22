"""Module for a reservoir model."""

import filecmp
import logging
import math
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union, get_args

import numpy as np
import scipy

import rtctools_simulation.reservoir.setq_help_functions as setq_functions
from rtctools_simulation.interpolate import fill_nans_with_interpolation
from rtctools_simulation.model import Model, ModelConfig
from rtctools_simulation.reservoir._input import (
    Input,
    OutflowType,
    input_to_dict,
)
from rtctools_simulation.reservoir._variables import (
    FixedInputVar,
    InputVar,
    OutputVar,
    QOutControlVar,
    SchemeVar,
    StateVar,
)
from rtctools_simulation.reservoir.minq import QMinParameters, QMinProblem
from rtctools_simulation.reservoir.rule_curve import rule_curve_deviation, rule_curve_discharge

DEFAULT_MODEL_DIR = Path(__file__).parent.parent / "modelica" / "reservoir"

logger = logging.getLogger("rtctools")


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
        # Stored parameters
        self.max_reservoir_area = 0  # Set during pre().
        # Model inputs and input controls.
        self._input = Input()
        self._allow_set_var = True
        self.initial_v = None
        self.initial_h = None

    def _get_lookup_table_equations(self, allow_missing_lookup_tables=True):
        return super()._get_lookup_table_equations(allow_missing_lookup_tables)

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
        for filename in [
            "reservoir.mo",
            "reservoir_minq.mo",
            "lookup_table_equations.csv",
        ]:
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

        self._copy_timeseries()
        initial_h = self._determine_initial_elevation()
        self._handle_missing_h_observed()
        self._process_input_variables(initial_h)
        self.max_reservoir_area = self.parameters().get("max_reservoir_area", 0)

    def _copy_timeseries(self):
        """Create a copy of timeseries which may be overwritten by the simulation."""
        timeseries_to_copy = ["H_observed", "rule_curve"]
        for timeseries in timeseries_to_copy:
            if timeseries in list(self.io.get_timeseries_names()):
                timeseries_input = self.get_timeseries(timeseries)
                self.set_timeseries(f"{timeseries}_input", timeseries_input.copy())

    def _determine_initial_elevation(self):
        """Determine the initial elevation based on available timeseries.

        To avoid infeasibilities, the default value for the elevation needs
        to be within the range of the lookup table.
        We use the intial volume or elevation to ensure this."""
        timeseries_names = self.io.get_timeseries_names()
        if "H_observed" in timeseries_names:
            initial_h = float(self.get_timeseries("H_observed")[0])
            logger.info("Using H_observed timeseries for initial elevation.")
        elif "H" in timeseries_names:
            initial_h = float(self.get_timeseries("H")[0])
            logger.info("Using H timeseries for initial elevation.")
        elif "V" in timeseries_names:
            initial_h = float(self._lookup_tables["h_from_v"](self.get_timeseries("V")[0]))
            logger.info("Using V timeseries for initial elevation.")
        else:
            raise Exception(
                'No initial condition is provided for reservoir elevation, "H", '
                'reservoir volume, "V", or observed elevation "H_observed". '
                "One of these must be provided."
            )
        # set the initial volume
        v_from_h = self.lookup_tables().get("v_from_h")
        if v_from_h is None:
            raise ValueError("The lookup table v_from_h is not found.")
        self.initial_v = float(v_from_h(initial_h))
        if "V" in timeseries_names and self.initial_v != self.get_timeseries("V")[0]:
            logger.warning(
                f"Initial elevation {initial_h} does not match the provided initial volume "
                f"{self.get_timeseries('V')[0]}. Initial volume will be overwritten."
            )
        volumes = np.full_like(self.times(), np.nan)
        volumes[0] = self.initial_v
        self.set_timeseries("V", volumes)
        return initial_h

    def _handle_missing_h_observed(self):
        """Save the first missing H_observed value for potential use in schemes."""
        timeseries_names = self.io.get_timeseries_names()
        if "H_observed" in timeseries_names:
            if np.any(np.isnan(self.get_timeseries("H_observed"))):
                h_timeseries = self.io.get_timeseries("H_observed")
                for x in range(len(h_timeseries[0])):
                    if np.isnan(h_timeseries[1][x]):
                        self.first_missing_Hobs = h_timeseries[0][x]
                        break

    def _process_input_variables(self, initial_h):
        """Process input variables and handle missing or NaN values."""
        timeseries_names = self.io.get_timeseries_names()
        input_vars = get_args(QOutControlVar) + get_args(FixedInputVar)
        default_values = {var: 0 for var in input_vars}
        default_values[InputVar.H_OBSERVED.value] = initial_h

        for var in input_vars:
            default_value = default_values[var]
            if var not in timeseries_names:
                self.set_timeseries(var, [default_value] * len(self.times()))
                logger.info(f"{var} not found in the input file. Setting it to {default_value}.")
                continue
            timeseries = self.get_timeseries(var)
            if var == InputVar.H_OBSERVED.value and np.isnan(timeseries[0]):
                timeseries[0] = initial_h
            if np.all(np.isnan(timeseries)):
                timeseries = [default_value] * len(self.times())
                logger.info(
                    f"{var} contains only NaNs in the input file. "
                    f"Setting these values to {default_value}."
                )
                continue
            logger.info(
                f"{var} contains NaNs in the input file. "
                f"Setting these values using linear interpolation."
            )
            timeseries = fill_nans_with_interpolation(self.times(), timeseries)
            self.set_timeseries(var, timeseries)

    # Helper functions for getting/setting the time/date/variables.
    def get_var(self, name: str) -> float:
        """
        Get the value of a given variable at the current time.

        :param var: name of the variable.
        :returns: value of the given variable.
        """
        try:
            value = super().get_var(name)
        except KeyError as error:
            expected_vars = list(InputVar) + list(OutputVar)
            message = f"Variable {name} not found. Expected var to be one of {expected_vars}."
            raise KeyError(message) from error
        return value

    def set_var(self, name: str, value):
        """
        Set the value of a given variable at the current time.

        :param name: variable name.
        :param value: value to set the variable with.
        :returns: value of the given variable.

        :meta private:
        """
        if not self._allow_set_var:
            raise ValueError("Do not set variables directly. Use schemes instead.")
        return super().set_var(name, value)

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
        lookuptable ``qspill_from_h``.
        """
        self._input.outflow.outflow_type = OutflowType.COMPOSITE
        self._input.outflow.components.do_spill = True

    def apply_adjust(self):
        """Scheme to adjust simulated volume to observed volume.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        Observed pool elevations (H_observed) can be provided to the model, internally these are
        converted to observed volumes (V_observed) via the lookup table ``h_from_v``.
        When applying this scheme, V is set to V_observed and a corrected version of the outflow,
        Q_out_corrected, is calculated in order to preserve the mass balance.
        """
        if self.get_current_time() == self.get_start_time():
            logger.debug(
                "Skip applying adjust at initial time, since no previous volume is available."
            )
            return
        current_step = int(self.get_current_time() / self.get_time_step())
        h_observed = self.get_timeseries("H_observed_input")[current_step]
        if np.isnan(h_observed):
            if np.all(np.isnan(self.get_timeseries("H_observed_input")[current_step:])):
                logger.debug(
                    f"Observed elevation is NaN for timestep {current_step} and all future "
                    "timesteps. Elevations will not be adjusted."
                )
                return
            else:
                logger.info(
                    f"Observed elevation not provided for timestep {current_step}. "
                    "Elevations will not be adjusted."
                )
                return
        q_out = self._get_q_out_for_h_target(h_observed)
        q_out = max(0, q_out)  # If outflow is negative, set outflow to zero.
        self._input.outflow.outflow_type = OutflowType.FROM_INPUT
        self._set_q(InputVar.Q_OUT, float(q_out))

    def _get_q_out_for_h_target(self, h_target) -> float:
        """Get the required outflow given a target elevation."""
        v_from_h = self.lookup_tables().get("v_from_h")
        if v_from_h is None:
            raise ValueError("The lookup table v_from_h is not found.")
        v_target = v_from_h(h_target)
        v_previous = self.get_var("V")
        t_current = self.get_current_time()
        dt = self.get_time_step()
        mm_per_hour_to_m_per_s = 1 / 3600 / 1000
        q_in = self.timeseries_at(InputVar.Q_IN.value, t_current)
        if self._input.rain_evap.include_evaporation:
            area_from_v = self.lookup_tables().get("area_from_v")
            if area_from_v is None:
                raise ValueError("The lookup table area_from_v is not found.")
            area = area_from_v(v_target)
            evap_mm_per_hour = self.timeseries_at(InputVar.Q_EVAP.value, t_current)
            q_evap = area * evap_mm_per_hour * mm_per_hour_to_m_per_s
        else:
            q_evap = 0
        if self._input.rain_evap.include_rain:
            rain_mm_per_hour = self.timeseries_at(InputVar.Q_RAIN.value, t_current)
            q_rain = self.max_reservoir_area * rain_mm_per_hour * mm_per_hour_to_m_per_s
        else:
            q_rain = 0
        q_out = q_in + q_rain - q_evap - (v_target - v_previous) / dt
        return q_out

    def apply_passflow(self):
        """Scheme to let the outflow be the same as the inflow.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.

        .. note:: This scheme cannot be used in combination with
            :py:meth:`.ReservoirModel.apply_poolq`, or :py:meth:`.ReservoirModel.set_q` when the
            target variable is Q_out.
        """
        self._input.outflow.outflow_type = OutflowType.PASS

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
        self._input.outflow.outflow_type = OutflowType.LOOKUP_TABLE

    def apply_fillspill(
        self,
    ) -> float:
        """
        Determines the outflow from the reservoir based on the inflow and minimum required
        outflow (downstream water demands or power generation objectives), as well as reservoir
        characteristics of maximum discharge of the dam facilities or operational rules
        (e.g. maximum generator discharge, maximum sluice discharge).
        Requires preconfigured parameters for ["Spillway_H", "Reservoir_Htarget", "Reservoir_Qmax",
        "Reservoir_Qmin"] in rtcParameterConfig.xml

        """
        if self.get_current_time() == self.get_start_time():
            logger.debug(
                "Skip applying fillspill at initial time, since no previous volume is available."
            )
            return
        current_h = self.get_var("H")
        inflow = self.get_var("Q_in")
        parameters = self.parameters()
        required_parameters = {
            "Spillway_H",
            "Reservoir_Htarget",
            "Reservoir_Qmax",
            "Reservoir_Qmin",
        }
        all_pars_present = [par in parameters.keys() for par in required_parameters]
        if not all(all_pars_present):
            raise KeyError(
                f"Not all parameters [{required_parameters}] for FILLSPILL"
                f"are configured in rtcParameterConfig.xml"
            )

        ## If stage exceeds hmax, apply spill and release as much as possible
        if current_h > parameters["Spillway_H"]:
            self.apply_spillway()
            self.set_q(
                target_variable="Q_turbine",
                input_type="parameter",
                input_data=parameters["Reservoir_Qmax"],
            )
        elif current_h >= parameters["Reservoir_Htarget"]:
            if inflow > parameters["Reservoir_Qmax"]:  ## discharge qlim, excess is added to storage
                self.set_q(
                    target_variable="Q_turbine",
                    input_type="parameter",
                    input_data=parameters["Reservoir_Qmax"],
                )
            elif (
                inflow <= parameters["Reservoir_Qmax"]
            ):  ## If inflow between qmin and qlim, pass it directly through the system
                self.apply_passflow()
        elif current_h < parameters["Reservoir_Htarget"]:  ## Use storage to supply minimum outflow
            self.set_q(
                target_variable="Q_turbine",
                input_type="parameter",
                input_data=parameters["Reservoir_Qmin"],
            )
        else:
            logger.warning(
                f"apply_fillspill : At model time {self.get_current_datetime()} "
                f"apply_fillspill was called but conditions of H_sim with value '{current_h}'"
                f" was such that no subscheme was applied and nothing has changed."
            )

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
        self._input.rain_evap.include_rain = True

    def include_evaporation(self):
        """Scheme to include the effect of evaporation on the reservoir volume.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        This scheme computes

            Q_evap = Area * mm_evaporation_per_hour / 3600 / 1000 * include_evaporation.

        This is then treated in the mass balance of the reservoir

            der(V) = Q_in - Q_out + Q_rain - Q_evap.
        """
        self._input.rain_evap.include_evaporation = True

    def include_rainevap(self):
        """Scheme to include the effect of both rainfall and evaporation on the reservoir volume.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        This scheme implements both :py:meth:`.ReservoirModel.include_rain`
        and :py:meth:`.ReservoirModel.include_evaporation`.
        """
        self._input.rain_evap.include_rain = True
        self._input.rain_evap.include_evaporation = True

    def apply_rulecurve(self, outflow: QOutControlVar = InputVar.Q_TURBINE, ignore_inflows=False):
        """Scheme to set the outflow of the reservoir in order to reach a rulecurve.

        This scheme can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        This scheme uses the lookup table ``v_from_h`` and requires the following parameters
        from the ``rtcParameterConfig.xml`` file.

            - ``rule_curve_q_max``: Upper limiting discharge while blending pool elevation
              (m^3/timestep)
            - ``rule_curve_blend``:  Number of timesteps over which to bring the pool back to the
              scheduled elevation.
            - ''ignore_inflows'' : Whether to ignore the inflow, and solely use
              current volume difference. Defaults to False

        The user must also provide a timeseries with the name ``rule_curve``. This contains the
        water level target for each timestep.

        :param outflow: :py:type:`~rtctools_simulation.reservoir._variables.QOutControlVar`
            (default: :py:type:`~rtctools_simulation.reservoir._variables.InputVar.Q_TURBINE`)
            outflow variable that is modified to reach the rulecurve.
        """
        if self.get_current_time() == self.get_start_time():
            logger.debug(
                "Skip applying rule curve at initial time, since no previous volume is available."
            )
            return
        outflow = InputVar(outflow)
        current_step = int(self.get_current_time() / self.get_time_step())
        q_max = self.parameters().get("Reservoir_Qmax") * self.get_time_step()  # V/timestep max
        if q_max is None:
            raise ValueError(
                "The parameter Reservoir_Qmax is not set, "
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
                "The lookup table v_from_h is not found It is required for the rule curve scheme."
            )
        volume_target = v_from_h_lookup_table(rule_curve[current_step])
        previous_volume = self.get_var("V")
        if not ignore_inflows:
            q_max -= self.timeseries_at("Q_in", self.get_current_time()) * self.get_time_step()
        if q_max < 0:
            logger.debug("Q_max is negative. Setting it to 0.")
            q_max = 0
        discharge = rule_curve_discharge(
            volume_target,
            previous_volume,
            q_max,
            blend,
        )
        discharge_per_second = discharge / self.get_time_step()
        if not ignore_inflows:
            discharge_per_second += self.timeseries_at("Q_in", self.get_current_time())
        self._set_q(outflow, max(0, float(discharge_per_second)))
        logger.debug(f"Rule curve function has set {outflow} to {discharge_per_second} m^3/s")

    def calculate_rule_curve_deviation(
        self,
        h_var: str = "H_observed",
        periods: int = 1,
        inflows: Optional[np.ndarray] = None,
        max_inflow: float = np.inf,
        maximum_difference: float = np.inf,
    ):
        """Calculate the moving average between the rule curve and a chosen elevation timeseries.

        This method can be applied inside :py:meth:`.ReservoirModel.pre` is calculating deviations
        with input timeseries.

        It can be applied in the :py:meth:`.ReservoirModel.calculate_output_variables` method
        to calculate deviations with the simulated timeseries.

        This method calculates the moving average between the rule curve and the simulated
        elevations over a specified number of periods. It takes the following parameters:

        :param h_var: The name of the elevation timeseries to compare with the rule curve.
            Default is "H_observed".
        :param periods: The number of periods over which to calculate the moving average.
        :param inflows: Optional. The inflows to the reservoir. If provided, the moving average
                        will be calculated only for the periods with non-zero inflows.
        :param max_inflow: Optional. The maximum inflow allowed while calculating a moving average.
                      Default is infinity, required if q_max is set.
        :param maximum_difference: Optional. The maximum allowable difference between the rule curve
                                   and the observed elevations.

        .. note:: The rule curve timeseries must be present in the timeseries import. The results
            are stored in the timeseries "rule_curve_deviation_<h_var>".
        """
        if not hasattr(self, "_io_output"):
            try:
                observed_elevations = self.io.get_timeseries(h_var)[1]
            except KeyError as exc:
                raise KeyError(f"The {h_var} timeseries is not found in the input file.") from exc
        else:
            observed_elevations = self.extract_results().get(h_var)
        try:
            rule_curve = self.io.get_timeseries("rule_curve")[1]
        except KeyError as exc:
            raise KeyError("The rule curve timeseries is not found in the input file.") from exc
        deviations = rule_curve_deviation(
            observed_elevations,
            rule_curve,
            periods,
            inflows=inflows,
            qin_max=max_inflow,
            maximum_difference=maximum_difference,
        )

        self.set_timeseries("rule_curve_deviation_" + h_var, deviations)
        if hasattr(self, "_io_output"):
            self.extract_results().update({"rule_curve_deviation_" + h_var: deviations})

    def calculate_single_cumulative_inflow(
        self,
        start_time: int = None,
        end_time: int = None,
    ):
        """Calculate the cumulative inflow over a specified time period. The default behaviour
        is to consider the period up to and including the current timestep.

        :param start_time: The starting timestep index of the period to sum over.
        :param end_time: The ending timestep index of the period to sum over.
        :returns: The sum of inflows over the specified time period."""
        if start_time is None:
            start_time = int(self.get_start_time())
        if end_time is None:
            end_time = int(self.get_current_time())
        dt = self.get_time_step()
        if dt is None:
            times = self.times()
            dt = times[1] - times[0]
            logger.debug("We assume a constant timestep size of %s", dt)
        if start_time < end_time:
            return sum(self.get_timeseries("Q_in")[start_time : end_time + 1]) * dt
        elif start_time == end_time:
            return self.get_timeseries("Q_in")[start_time] * dt
        else:
            logger.warning(
                "In function calculate_single_cumulative_inflow: start_time must be less and or "
                "equal to end_time"
            )
            return None

    def calculate_cumulative_inflows(self):
        """Calculate the cumulative inflows over the entire simulation period.

        This can be called in ``pre``. Reults are saved to the timeseries
        ``cumulative_inflows``."""
        inflows = self.get_timeseries("Q_in")
        cumulative_inflows = np.zeros_like(inflows)
        for i in range(len(cumulative_inflows)):
            cumulative_inflows[i] = self.calculate_single_cumulative_inflow(
                start_time=0, end_time=i
            )
        self.set_timeseries("cumulative_inflows", cumulative_inflows)
        return cumulative_inflows

    def get_flood_flag(
        self,
        q_out_daily_average: float,
        flood_elevation: float,
    ):
        """Preprocessing step which determines and returns a flag for flooding. Can be called during
        ``pre``.

        Indicative elevations are calculated using inflows (``Q_in``) and averge daily outflows.
        If any indicative elevation is above the flood elevation, a the flood flag is set to True.

        :param Q_out_daily_average: The average outflow over a 24 hour period (m^3/s).
        :param flood_elevation: The elevation above which flooding occurs (m).
        :returns: A boolean flag indicating whether flooding occurs (True) or not (False).
        """
        q_in_ts = self.get_timeseries("Q_in")
        # convert the daily average outflow to a timestep outflow.
        dt = self.get_time_step()
        if dt is None:
            times = self.times()
            dt = times[1] - times[0]
            logger.debug("We assume a constant timestep size of %s", dt)
        q_out = q_out_daily_average
        # for each timestep calculate the volume of the reservoir given the inflow and outflow
        volumes = np.zeros_like(q_in_ts)
        volumes[0] = self.initial_v
        for i in range(1, len(q_in_ts)):
            volumes[i] = volumes[i - 1] + (q_in_ts[i] - q_out) * dt
        # convert volumes to elevations
        h_from_v = self.lookup_tables().get("h_from_v")
        if h_from_v is None:
            raise ValueError("The lookup table h_from_v is not found.")
        elevations = np.zeros_like(volumes)
        for i in range(len(volumes)):
            elevations[i] = h_from_v(volumes[i])
        # check if any elevation is above the flood elevation
        flood_flag = any(elevation > flood_elevation for elevation in elevations)
        return flood_flag

    def adjust_rulecurve(
        self,
        periods: int,
        h_var: str = "H_observed",
        application_time: Optional[np.datetime64] = None,
        extrapolate_trend_linear: Optional[bool] = False,
    ):
        """
        Adjusts the rulecurve based on deviations compared to H_observed.

        This method can be applied inside :py:meth:`.ReservoirModel.pre`.

        :param periods: The number of periods over which to calculate the moving average.
        :param h_var: The name of the elevation timeseries to adjust the rulecurve.
        :param application_time: Optional. Time at which to start applying the correction.
        :param extrapolate_trend_linear: Bool. Option to extrapolate a trend in the
          deviations to the rulecurve.

        The function overwrites the required timeseries of 'rule_curve', and should be
        called in self.apply_schemes()
        """
        if application_time is None:
            try:
                application_time = self.first_missing_Hobs
                logger.info(
                    'Setting application time for function "adjust_rulecurve" '
                    'to the first missing value in input timeseries "H_observed" '
                    f"which is {application_time}"
                )
            except AttributeError as err:
                raise AttributeError(
                    "Application time is not provided for 'adjust_rulecuve'"
                    " and no missing observations can be found to find a "
                    "starting point. Configuration of the application time "
                    "is required."
                ) from err

        deviations = self.io.get_timeseries("rule_curve_deviation_" + h_var)
        index_time = [deviations[0][x] < application_time for x in range(len(deviations[0]))]
        deviations = deviations[1][index_time]
        first_dev, last_dev = deviations[periods - 1], deviations[-1]
        rule_curve = self.io.get_timeseries("rule_curve")[1]
        future_deviations = np.full(shape=(len(rule_curve) - len(deviations)), fill_value=last_dev)
        if extrapolate_trend_linear:
            trend = (last_dev - first_dev) / (len(deviations) - 1)
            trend_difference = np.linspace(
                trend, len(future_deviations) * trend, len(future_deviations)
            )
            future_deviations += trend_difference
        rule_curve[-len(future_deviations) :] += future_deviations
        self.io.set_timeseries("rule_curve", self.io.get_timeseries("rule_curve")[0], rule_curve)

    def _set_q(self, q_var: QOutControlVar, value: float):
        """Set an outflow control variable."""
        if q_var == InputVar.Q_OUT:
            self._input.outflow.outflow_type = OutflowType.FROM_INPUT
            self._input.outflow.from_input = value
        elif q_var == InputVar.Q_TURBINE:
            self._input.outflow.outflow_type = OutflowType.COMPOSITE
            self._input.outflow.components.turbine = value
        elif q_var == InputVar.Q_SLUICE:
            self._input.outflow.outflow_type = OutflowType.COMPOSITE
            self._input.outflow.components.sluice = value
        else:
            raise ValueError(f"Outflow shoud be one of {get_args(QOutControlVar)}.")

    def apply_minq(
        self,
        *,
        h_target: Union[float, Iterable[float], str],
        h_min: float = 0,
        h_max: Optional[float] = None,
        q_flood: Optional[float] = 0,
        recalculate: bool = False,
    ):
        """
        Determine and use outflow with a minimal peak.

        The outflow is minimized for the given optimization parameters.
        If recalculate is True, the minimzed outflow will be recalculated.
        This is useful if some of the parameters like h_target have changed.

        :param h_target: float, Iterable[float], str.
            Target elevation. Can be the name of a timeseries.
        :param h_min: float, optional.
            Minimum elevation. Default is 0.
        :param h_max: float, optional.
            Maximum elevation. Default is no None (no maximum elevation).
        :param q_flood: float, optional.
            Flood discharge. When computing the peak outflow,
            values below the flood discharge are ignored.
        :param recalculate: bool, optional.
            If True, the outflow will be recalculated. Default is False.
        """
        self._input.outflow.outflow_type = OutflowType.FROM_INPUT
        if self.get_current_time() == self.get_start_time():
            # Q_out at the start time will have no affect, so we can set it to zero.
            # Optimization is not possible, since not all states have been initialized.
            self._input.outflow.from_input = 0
            return
        name = "Q_out_minq"
        if name not in self.io.get_timeseries_names() or recalculate:
            if isinstance(h_target, str):
                h_target = self.get_timeseries(h_target)
            v_from_h = self.lookup_tables().get("v_from_h")
            if v_from_h is None:
                raise ValueError("The lookup table v_from_h is not found.")
            params = QMinParameters(
                v_min=v_from_h(h_min),
                v_max=v_from_h(h_max),
                v_target=v_from_h(h_target).toarray().flatten(),
                q_flood=q_flood,
            )
            self._calculate_qmin(params=params, name=name)
        q_out = self.timeseries_at(name, self.get_current_time())
        self._input.outflow.from_input = q_out

    def _calculate_qmin(self, params: QMinParameters, name: str):
        """
        Calculate the optimized outflow for the Q_min scheme.

        Store the result in the timeseries with the given name.
        """
        times_sec = self.times()
        datetimes = [self.io.sec_to_datetime(t, self.io.reference_datetime) for t in times_sec]
        self._input.outflow.outflow_type = OutflowType.FROM_INPUT
        input_timeseries = self._get_optimization_input_timeseries(times_sec)
        config = deepcopy(self._config)
        config.set_model("ReservoirMinQ")
        problem = QMinProblem(
            config=config,
            datetimes=datetimes,
            params=params,
            input_timeseries=input_timeseries,
        )
        success = problem.optimize()
        if not success:
            raise ValueError("Solving minimal peak outflow did not succeed.")
        results = problem.extract_results()
        var = OutputVar.Q_OUT.value
        values = results[var]
        self.set_timeseries(name, values)

    def _get_optimization_input_timeseries(self, times_sec: List[int]) -> Dict[str, list]:
        """Get timeseries to use for optimization."""
        input_vars = {}
        for var in get_args(FixedInputVar):
            values = [self.timeseries_at(var.value, t) for t in times_sec]
            input_vars[var] = values
        index_first_time_stamp = list(self.times()).index(times_sec[0])
        nans = [np.nan for t in times_sec if t >= self.get_current_time()]
        results = self.extract_results()
        for var in get_args(StateVar):
            values = list(results[var.value])[index_first_time_stamp:]
            input_vars[var] = values + nans
        modelica_vars = input_to_dict(self._input)
        for var in get_args(SchemeVar):
            input_vars[var] = [modelica_vars[var] for _ in times_sec]
        t0 = self.io.reference_datetime
        days = [self.io.sec_to_datetime(time, t0).day for time in times_sec]
        input_vars[InputVar.DAY] = days
        return input_vars

    # Methods for applying schemes / setting input.
    def set_default_input(self):
        """Set default input values.

        This method sets default values for internal variables at each timestep.
        This is important to ensure that the schemes behave as expected.

        :meta private:
        """
        self._input = Input()
        self._input.volume.h_observed = self.get_var(InputVar.H_OBSERVED.value)
        self._input.inflow = self.get_var(InputVar.Q_IN.value)
        self._input.rain_evap.mm_evaporation_per_hour = self.get_var("mm_evaporation_per_hour")
        self._input.rain_evap.mm_rain_per_hour = self.get_var("mm_rain_per_hour")
        self._input.outflow.components.turbine = self.get_var("Q_turbine")
        self._input.outflow.components.sluice = self.get_var("Q_sluice")
        self._input.outflow.from_input = self.get_var("Q_out_from_input")
        self._input.day = self.get_current_datetime().day

    def apply_schemes(self):
        """
        Apply schemes.

        This method is called at each timestep and should be implemented by the user.
        This method should contain the logic for which scheme is applied under which conditions.

        :meta private:
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

        :meta private:
        """
        self._allow_set_var = False
        self.set_default_input()
        self.apply_schemes()
        self._allow_set_var = True
        self._set_modelica_input()

    def _set_modelica_input(self):
        """Set the Modelica input variables."""
        # Validate model input.
        self._input = Input(**self._input.model_dump())
        # Set Modelica inputs.
        modelica_vars = input_to_dict(self._input)
        for var, value in modelica_vars.items():
            self.set_var(var.value, value)

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
        target_variable: QOutControlVar = InputVar.Q_TURBINE,
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

        :param target_variable: :py:type:`~rtctools_simulation.reservoir._variables.QOutControlVar`
            (default: :py:const:`~rtctools_simulation.reservoir._variables.InputVar.Q_TURBINE`)
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
        target_variable = InputVar(target_variable)
        target_value = setq_functions.getq(
            self,
            target_variable,
            input_type,
            apply_func,
            input_data,
            timestep,
            nan_option,
        )
        self._set_q(target_variable.value, target_value)

    def find_maxq(self, discharge_relation: str, solve_guess: Optional[float] = np.nan):
        """
        Utility to calculate the theoretical maximum discharge out of the reservoir.
        Supports 3 different methods for 'discharge_relation'

        :param discharge_relation: str
            The method used to calculate the maximum possible discharge maxq, options are

                - 'Spillway': maxq based on spillway Q/H + fixed Qmax. Requires parameter
                  'Reservoir_Qmax', as well as lookup_table 'qspill_from_h'.
                - 'Fixed': maxq based on fixed discharge only. Requires parameter
                  'Reservoir_Qmax'.
                - 'Tailwater': maxq is influenced by tailwater. Three lookup tables are required:
                  ``qspill_from_h`` (spillway lookup table), ``qnotspill_from_dh`` (head vs
                  (Qout-Qspill) lookup table) and ``qtw_from_tw`` (tailwater elevation vs discharge
                  curve). maxq is calculated by determining Qspill based on the simulated elvation,
                  and then using a solver to determine the intersection of the remaining lookup
                  tables using the function ``_find_maxq_tailwater``.

        :param solve_guess: Optional[float] (default: np.nan)
            Initial guess for the solver when using the 'Tailwater' method. Defaults to current
            reservoir elevation in the supporting function
            :py:meth:`.ReservoirModel._find_maxq_tailwater` when it is np.nan.

        This utility can be applied inside :py:meth:`.ReservoirModel.apply_schemes`.
        """
        supported_relations = ["Spillway", "Fixed", "Tailwater"]
        if discharge_relation not in supported_relations:
            raise KeyError(
                f" At timestep {self.get_current_datetime()}:"
                f'Utility find_maxq has an invalid argument. "{discharge_relation}"'
                f"is not one of the supported discharge relations. "
                f"Choose one of {supported_relations}"
            )
        latest_h = self.get_var("H")

        if discharge_relation == "Spillway":
            try:
                q_from_h = self.lookup_tables().get("qspill_from_h")
            except Exception as e:
                logger.warning(
                    f" At timestep {self.get_current_datetime()}:"
                    f"Utility find_maxq is not able to compute spill from h."
                    f"qspill_from_h cannot be found."
                )
                raise ValueError("find_maxq: lookup_table qspill_from_h is not present") from e
            spill_q = q_from_h(latest_h)
            if "Reservoir_Qmax" not in self.parameters():
                raise KeyError(
                    "find_maxq can not access parameter"
                    "'Reservoir_Qmax' in rtcParameterConfig.xml"
                )
            maxq = spill_q + self.parameters()["Reservoir_Qmax"]
        elif discharge_relation == "Fixed":
            if "Reservoir_Qmax" not in self.parameters():
                raise KeyError(
                    "find_maxq can not access parameter"
                    '"Reservoir_Qmax" in rtcParameterConfig.xml'
                )
            maxq = self.parameters()["Reservoir_Qmax"]
        elif discharge_relation == "Tailwater":
            if np.isnan(solve_guess):
                solve_guess = latest_h
            maxq = self._find_maxq_tailwater(latest_h, solve_guess)
        return max(0, maxq)

    def _find_maxq_tailwater(self, latest_h: float, solve_guess: float):
        """
        Supporting function for utility ``find_maxq``. Requires presence of 3 lookup tables.
            - ``qspill_from_h``: Qspill as function of pool elevation
            - ``qnotspill_from_dh``: Maximum non-spillway discharge as a function of head difference
            - ``qtw_from_tw``: Downstream discharge as function of tailwater elevation.

        :param latest_h: float
            Current reservoir elevation

        :param solve_guess: float
            Initial TW elevation guess for increased solver performance.
        """
        try:
            qs_from_h = self.lookup_tables().get("qspill_from_h")
            qnotspill_from_dh = self.lookup_tables().get("qnotspill_from_dh")
            qtw_from_tw = self.lookup_tables().get("qtw_from_tw")
        except Exception as e:
            logger.warning(
                f" At timestep {self.get_current_datetime()}:"
                f"Utility find_maxq is not able to compute spill from h."
                f"Not all required lookup tables are found."
            )
            raise ValueError("find_maxq: Not all lookup tables are present") from e

        q_spill = qs_from_h(latest_h)

        def qmax_func(tw_solve, h_res, q_spill):
            tw = tw_solve[0]  # fsolve passes arrays
            q_upstream = qnotspill_from_dh(h_res - tw) + q_spill  ## Water release needs to equal
            q_downstream = qtw_from_tw(tw)  ## Downstream water flux
            return [float(q_upstream - q_downstream)]  # fsolve wants arrays

        result = scipy.optimize.fsolve(
            lambda tw: qmax_func(tw, latest_h, q_spill), x0=[solve_guess]
        )
        qmax = qtw_from_tw(result)
        return max(0, qmax)
