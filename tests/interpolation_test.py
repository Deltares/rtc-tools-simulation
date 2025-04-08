"""Module for testing the interpolation module."""

import numpy as np
import pytest

from rtctools_simulation.interpolate import fill_nans_with_interpolation


@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([10, 20, 30], [1, 2, np.nan], [1, 2, 2]),
        ([10, 20, 30], [1, np.nan, 3], [1, 2, 3]),
        ([10, 20, 30], [np.nan, 2, 3], [2, 2, 3]),
        ([10, 20, 30], [1, np.nan, np.nan], [1, 1, 1]),
        ([10, 20, 30], [np.nan, 2, np.nan], [2, 2, 2]),
        ([10, 20, 30], [np.nan, np.nan, 3], [3, 3, 3]),
        ([10, 20, 30], [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]),
    ],
)
def test_fill_nans_with_inetrpolation(x, y, expected):
    """Test fill_nans_with_interpolation."""
    x = np.array(x)
    y = np.array(y)
    y_old = y.copy()
    expected = np.array(expected)
    y_new = fill_nans_with_interpolation(x, y)
    np.testing.assert_array_almost_equal(y, y_old)
    np.testing.assert_array_almost_equal(y_new, expected)
