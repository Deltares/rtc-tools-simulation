"""Contains the rule curve deviation function to compute the average deviation between the
rule curve elevation and the observed pool elevation."""

from typing import Optional

import numpy as np


def rule_curve_deviation(
    observed_elevations: np.ndarray,
    rule_curve: np.ndarray,
    periods: int,
    inflows: Optional[np.ndarray] = None,
    q_max: float = np.inf,
    maximimum_difference: float = np.inf,
) -> np.ndarray:
    """
    Computes an adjusted moving average of the deviation between the observed pool elevation and
    the rule curve elevation. Deviations at timesteps where the inflow exceeds the maximum inflow
    are set to the maximimum_difference. Deviations that exceed the maximum deviation
    are also set to the maximimum_difference.

    :param observed_elevations: np.ndarray
        The observed pool elevations [m].
    :param rule_curve: np.ndarray
        The rule curve [m].
    :param periods: int
        The number of periods to calculate the average deviation over.
    :param inflows: np.ndarray (optional)
        The inflows [m^3/s], required if q_max is not np.inf.
    :param q_max: float (optional)
        The maximum inflow.
    :param maximimum_difference: float (optional)
        The maximum absolute deviation per timestep.

    :return: np.ndarray
        The average deviation for each timestep.
    """
    if len(observed_elevations) != len(rule_curve):
        raise ValueError("The observed elevations and pool elevations should have the same length.")
    if np.any(np.isnan(observed_elevations)):
        raise ValueError("The observed elevations should not contain NaN values.")
    if periods < 1:
        raise ValueError("The number of periods should be at least 1.")
    if periods > len(observed_elevations):
        raise ValueError(
            "The number of periods cannot be larger than the number of observed elevations."
        )
    if q_max != np.inf and inflows is None:
        raise ValueError("The inflows should be provided if the maximum inflow is set.")
    deviation_array = observed_elevations - rule_curve
    deviation_array = np.where(
        abs(deviation_array) > maximimum_difference,
        np.full(len(deviation_array), maximimum_difference),
        deviation_array,
    )
    if inflows is not None:
        deviation_array = np.where(
            inflows > q_max, np.full(len(deviation_array), 0), deviation_array
        )

    average_deviation = np.full(len(observed_elevations), np.nan)
    for i in range(periods, len(rule_curve) + 1):
        average_deviation[i - 1] = sum(deviation_array[i - periods : i]) / periods
    return average_deviation
