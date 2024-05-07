"""
Rule curve module for reservoir operation.
------------------------------------------
"""

import logging

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
    return max(min(required_flow, q_max), 0)
