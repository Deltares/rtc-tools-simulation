"""Module for interpolating data."""

import numpy as np


def fill_nans_with_interpolation(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Given an xy-curve, replace NaNs in y with linearly interpolated values."""
    nans = np.isnan(y)
    if (~nans).sum() == 0:
        return y
    if (~nans).sum() == 1:
        y[nans] = x[~nans]
        return y
    y[nans] = np.interp(x[nans], x[~nans], y[~nans])
    return y
