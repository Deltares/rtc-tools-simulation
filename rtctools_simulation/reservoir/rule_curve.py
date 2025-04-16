"""
Rule curve module for reservoir operation.
------------------------------------------
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger("rtctools")


def rule_curve_discharge(
    target_volume: float,
    current_volume: float,
    q_max: float = np.inf,
    blend: int = 1,
) -> float:
    """
    Determines the required outflow such that the current_volume becomes equal to the target_volume
    in `blend` number of timesteps. Note that it does not consider the inflows to the reservoir.
    As a result, the resulting volume may differ from the target.

    :param target_volume: float
        Target pool volume [m^3].
    :param current_volume: float
        Actual pool volume [m^3]
    :param blend: int
        Number of timesteps over which to bring the pool back to the scheduled elevation.
    :param q_max: float
        Upper limiting discharge while blending pool elevation [m^3/timestep].

    :return: float
        The required outflow [m^3/timestep].
    """
    if blend < 1:
        raise ValueError("The rule curve blend parameter should be at least 1.")
    if q_max < 0:
        raise ValueError("The rule curve maximum discharge parameter should be non-negative.")
    volume_difference = current_volume - target_volume
    required_flow = volume_difference / blend
    return min(required_flow, q_max)


def rule_curve_deviation(
    observed_elevations: np.ndarray,
    rule_curve: np.ndarray,
    periods: int,
    inflows: Optional[np.ndarray] = None,
    qin_max: float = np.inf,
    maximum_difference: float = np.inf,
) -> np.ndarray:
    """
    Computes a moving average of the deviation between the observed pool elevation and
    the rule curve elevation. Deviations at timesteps where the inflow exceeds the maximum inflow
    are set to 0. Deviations that exceed the maximum deviation are also set to the 0.

    :param observed_elevations: np.ndarray
        The observed pool elevations [m].
    :param rule_curve: np.ndarray
        The rule curve [m].
    :param periods: int
        The number of periods to calculate the average deviation over.
    :param inflows: np.ndarray (optional)
        The inflows [m^3/s], required if q_max is not np.inf.
    :param qin_max: float (optional)
        The maximum inflow.
    :param maximum_difference: float (optional)
        The maximum absolute deviation per timestep.

    :return: np.ndarray (same shape as rule_curve)
        The average deviation for each timestep.
    """
    if periods < 1:
        raise ValueError("The number of periods should be at least 1.")
    if periods > len(observed_elevations):
        raise ValueError(
            "The number of periods cannot be larger than the number of observed elevations."
        )
    if qin_max != np.inf and inflows is None:
        raise ValueError("The inflows should be provided if the maximum inflow is set.")
    deviation_array = observed_elevations - rule_curve
    deviation_array = np.where(
        abs(deviation_array) > maximum_difference, 0, deviation_array
    )  # Alternative: 0 -> maximum_difference
    if inflows is not None:
        deviation_array = np.where(inflows > qin_max, 0, deviation_array)

    average_deviation = np.full(len(rule_curve), np.nan)
    for i in range(periods, len(observed_elevations) + 1):
        if not np.sum(np.isnan(deviation_array[i - periods : i])) > (periods / 2):
            average_deviation[i - 1] = np.nanmean(deviation_array[i - periods : i])
        else:  ## Check for count of missing data in moving window
            average_deviation[i - 1] = 0
            logger.warning(
                "Rule_curve_deviation: more than half of observed elevations in "
                f'moving window of size {periods} are missing, deviation defaults to value of "0"'
            )
    return average_deviation
