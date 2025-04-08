"""Module for interpolating data."""

import numpy as np


def fill_nans_with_interpolation(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Given an xy-curve, replace NaNs in y with linearly interpolated values."""
    y_new = y.copy()
    nans = np.isnan(y)
    if (~nans).sum() == 0:
        return y_new
    if (~nans).sum() == 1:
        y_new[nans] = y[~nans]
        return y_new
    y_new[nans] = np.interp(x[nans], x[~nans], y[~nans])
    return y_new
