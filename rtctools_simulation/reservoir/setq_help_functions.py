"""
SetQ module for reservoir operation.
------------------------------------
"""

import logging

import numpy as np
from rtctools.simulation.simulation_problem import SimulationProblem

logger = logging.getLogger("rtctools")


class NoDataException(Exception):  ## noqa N818
    pass


def _find_prev_value(input_data, timestep, method="PREV"):
    """Function to find the previous non-nan data point from the given timeseries
    :param input_data: timeseries (list)
    :param timestep: timestep (index) at which to start within input_data (int)
    :param method: direction to search for the data point. If 'NEXT', we reverse the operation

    :return: previous non-NaN data point from the given timeseries
    """
    if method == "NEXT":  ## Invert input_data and remap t to the mirrored end of the timeseries
        input_data = input_data[::-1]
        timestep = len(input_data) - 1 - timestep
    target_value = np.nan
    i = 0  ## Iterable that will be deducted from timestep
    while np.isnan(target_value):
        i += 1
        if (timestep - i) >= 0:
            target_value = input_data[timestep - i]
        else:
            error_msg = "setq: There is no valid value in the timeseries with this nan_option"
            raise NoDataException(error_msg)
    res = {"value": target_value, "dist": i}
    return res


def _find_closest_value(back: dict, fwd: dict):
    """Function to find the closest value

    :param back
    :param fwd

    :return: target_value
    """
    target_value = np.nan
    if back["dist"] < fwd["dist"]:
        target_value = back["value"]
    elif back["dist"] > fwd["dist"]:
        target_value = fwd["value"]
    elif back["dist"] == fwd["dist"]:
        target_value = (back["value"] + fwd["value"]) / 2

    return target_value


def _find_back_and_fwd(input_data: list, timestep: int):
    """function to catch unique case of data only available on 1 side of t, without breaking

    :param input_data
    :param timestep
    :returns:

    """
    ## Needs to catch unique case of data only available on 1 side of t, without breaking.
    if not all(
        np.isnan(input_data[timestep:])
    ):  ## If fwd has no data, appoint bwd to the variable.
        fwd = _find_prev_value(input_data, timestep, "NEXT")
    else:
        fwd = _find_prev_value(input_data, timestep, "PREV")
    if not all(
        np.isnan(input_data[:timestep])
    ):  ## If bwd has no data, appoint fwd to the variable.
        back = _find_prev_value(input_data, timestep, "PREV")
    else:
        back = fwd
    return back, fwd


def _find_nonnan_value(input_data, timestep: int = None, method="CLOSEST"):
    """
    Function that allows the user to find a suitable (non-NaN) value in the supplied timeseries.

    :param method: str
        Options for method are:
            - 'CLOSEST' (default) : Finds the closest (time-wise) value. If they are the same
              distance, returns the interpolated value
            - 'PREV': Finds the closest value that occurred before the given timestep
            - 'NEXT': Finds the closest value that occurred after the given timestep
            - 'INTERP': Interpolates between the two closest valid timesteps. If only
              data is available to one side of 't', return closest value
    :return: target_value
        This is
    """
    if all(np.isnan(input_data)):
        raise NoDataException("Target_data is completely NaN")
    if method in ["PREV", "NEXT"]:
        target_value = _find_prev_value(input_data, timestep, method)["value"]
    elif method in ["CLOSEST", "INTERP"]:
        back, fwd = _find_back_and_fwd(input_data, timestep)

        if back["value"] == fwd["value"]:
            target_value = back["value"]
        elif method == "CLOSEST":
            target_value = _find_closest_value(back, fwd)
        elif method == "INTERP":
            distance = fwd["dist"] + back["dist"]
            diff = fwd["value"] - back["value"]
            ## Interpolation, with closest previous step as reference point
            target_value = back["value"] + (back["dist"] / distance) * diff
    else:
        raise Exception(f'Given method "{method}" is not a valid option')
    return target_value


def _getq_from_ts(
    input_data=None,
    timestep: int = None,
    input_data_name: str = "def_name",
    target_variable: str = "Q_release",
    apply_func="MEAN",
    nan_option=None,
):
    if apply_func == "INST":
        target_value = input_data[timestep]
        if np.isnan(target_value):
            if nan_option is None:
                error_msg = (
                    f'setq detects a NaN at time "{timestep}" in target data "{input_data_name}" '
                    f'when setting "{target_variable}" and there is no option set to treat this.'
                )
                logger.error(error_msg)
                raise NoDataException(error_msg)
            elif nan_option in ["PREV", "NEXT", "CLOSEST", "INTERP"]:
                target_value = _find_nonnan_value(input_data, timestep, nan_option)
            elif nan_option == "MEAN":
                target_value = np.nanmean(input_data)
            else:
                raise Exception("There is no suitable nan_option selected")
    ## If apply_func != INST, we can do simple operations on input_data.
    elif apply_func == "MEAN":
        target_value = np.nanmean(input_data)
    elif apply_func == "MIN":
        target_value = np.nanmin(input_data)
    elif apply_func == "MAX":
        target_value = np.nanmax(input_data)
    else:
        error_msg = f'setq: selected apply_func : "{apply_func}" is not recognized'
        logger.error(error_msg)
        raise Exception(error_msg)
    return target_value


def _preprocess_input_setq(
    model: SimulationProblem,
    target_value,
    target_variable: str = "Q_release",
    input_type: str = "timeseries",
    input_data=None,
    input_data_name="test_name",
):
    if isinstance(input_data, str):  ## Get timeseries from internal process
        if input_type == "timeseries":
            input_data_name = input_data
            input_data = model.io.get_timeseries(input_data)[1]  ## Get index 1 for value timeseries
        if input_type == "parameter":  ## Get value from internal process
            target_value = model.parameters()[input_data]
            input_data_name = input_data
    elif any([isinstance(input_data, float), isinstance(input_data, int)]):
        input_data_name = target_variable
        target_value = input_data
    elif isinstance(input_data, list):
        input_is_numeric = [
            isinstance(x_t, (int, float)) for x_t in np.nan_to_num(input_data).tolist()
        ]
        if all(input_is_numeric):
            input_data_name = target_variable
        else:
            raise Exception("List contains entries other than floats, integers and NaNs")
    return [input_data, input_data_name, target_value]


def getq(
    model: SimulationProblem,
    target_variable: str = "Q_turbine",
    input_type: str = "timeseries",
    apply_func: str = "MEAN",
    input_data: str = None,
    timestep: int = None,
    nan_option: str = None,
) -> float:
    """
    Get one of the input or output discharges to a given value,
    or a value determined from an input list.

    :param Model: object
        Reservoir Model
    :param target_variable: str (default: 'Q_turbine')
        The variable that is to be set.
    :param input_data: str
        the name of the target data. If not provided, it is set to the name of the target_variable.
        Name of timeseries_ID/parameter_ID in .xml file
    :param input_type: str (default: 'timeseries')
        The type of target data. Either 'timeseries' or 'parameter'. If it is a timeseries,
        the timeseries is assumed to have a regular time interval.
    :param apply_func: str
        Function that is used to find the fixed_value if input_type = 'timeseries'.
            - 'MEAN' (default): Finds the average value, excluding nan-values.
            - 'MIN': Finds the minimum value, excluding nan-values.
            - 'MAX': Finds the maximum value, excluding nan-values.
            - 'INST': Finds the value marked by the corresponding timestep 't'. If the
              selected value is NaN, nan_option determines the procedure to find a valid value.
    :param timestep:
        The timestep at which the input data should be read at if input_type = 'timeseries',
        the default is the current timestep of the simulation run.
    :param nan_option: the user can indicate the action to be take if missing values are found.
        Can be used in combination with input_type = 'timeseries' and apply_func = 'INST'.
            - 'MEAN': It will take the mean of the timeseries excluding nans.
            - 'PREV': It attempts to find the closest previous valid data point.
            - 'NEXT':  It attempts to find the closest next valid data point.
            - 'CLOSEST': It attempts to find the closest valid data point, either backwards or
              forward. If same distance, take average.
            - 'INTERP': Interpolates linearly between the closest forward and backward data points.

    :return: target value.
    """
    target_variable = target_variable.name
    target_value = np.nan  ## Set as default result
    ## Checks to process input_data into a consistent format (list/single value)
    input_data, input_data_name, target_value = _preprocess_input_setq(
        model, target_value, target_variable, input_type, input_data
    )
    if timestep is None and input_type == "timeseries" and apply_func == "INST":
        ## If no t is given, default to current timestep
        timestep = int(model.get_current_time() // model.get_time_step())
    if input_type == "timeseries":
        target_value = _getq_from_ts(
            input_data, timestep, input_data_name, target_variable, apply_func, nan_option
        )
    elif input_type == "parameter":
        target_value = _setq_from_parameter(
            target_value, nan_option, input_data_name, target_variable
        )
    else:
        raise ValueError("Argument input_type should be either `timeseries` or `parameter`.")
    if np.isnan(target_value):
        logger.error(
            f'setq was completed with a NaN value as result. "{model.get_var(target_variable)}"'
            f" is now NaN"
        )
    return target_value


def _setq_from_parameter(target_value, nan_option, input_data_name, target_variable) -> float:
    """
    Use setq function to fix functionality to a minimum value. This increases user-friendliness.
    For documentation, see setq

    :return: updated target value.
    """
    if np.isnan(target_value):
        if nan_option is None:
            logger.error(
                f'setq detects a nan for "{input_data_name}" when setting'
                f' "{target_variable} and there is no option given to treat this."'
            )
        else:
            logger.error(
                f'setq detects a nan for "{input_data_name}" when setting '
                f'"{target_variable} and option "{nan_option}" is not able to treat this.'
            )
    return target_value
