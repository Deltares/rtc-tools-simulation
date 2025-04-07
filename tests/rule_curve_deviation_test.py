"""Tests for rule_curve_deviation function."""

import numpy as np
import pytest

from rtctools_simulation.reservoir.rule_curve import (
    rule_curve_deviation,
)

test_data = [
    {  # Test whether zero difference gives zero average deviation
        "observed_elevations": np.array([10, 10, 10, 10, 10]),
        "rule_curve": np.array([10, 10, 10, 10, 10]),
        "periods": 1,
        "inflows": np.array([0, 0, 0, 0, 0]),
        "qin_max": np.inf,
        "maximum_difference": np.inf,
        "expected": np.array([0, 0, 0, 0, 0]),
    },
    {  # Test whether non-zero difference gives non-zero average deviation
        "observed_elevations": np.array([10, 10, 10, 10, 10]),
        "rule_curve": np.array([20, 20, 20, 20, 20]),
        "periods": 2,
        "inflows": np.array([0, 0, 0, 0, 0]),
        "qin_max": np.inf,
        "maximum_difference": np.inf,
        "expected": np.array([np.nan, -10, -10, -10, -10]),
    },
    {  # Test on increasing rule curve.
        "observed_elevations": np.array([10, 10, 10, 10, 10]),
        "rule_curve": np.array([10, 20, 30, 40, 50]),
        "periods": 2,
        "inflows": np.array([0, 0, 0, 0, 0]),
        "qin_max": np.inf,
        "maximum_difference": np.inf,
        "expected": np.array([np.nan, -5, -15, -25, -35]),
    },
    {  # Test whether exceecing the max inflow gives zero average deviation.
        "observed_elevations": np.array([10, 10, 10, 10, 10]),
        "rule_curve": np.array([20, 20, 20, 20, 20]),
        "periods": 2,
        "inflows": np.array([10, 10, 10, 10, 10]),
        "qin_max": 1,
        "maximum_difference": np.inf,
        "expected": np.array([np.nan, 0, 0, 0, 0]),
    },
    {  # Test whether only a single deviation is zeroed.
        "observed_elevations": np.array([10, 10, 10, 10, 10]),
        "rule_curve": np.array([20, 20, 20, 20, 20]),
        "periods": 2,
        "inflows": np.array([10, 10, 0, 10, 10]),
        "qin_max": 1,
        "maximum_difference": np.inf,
        "expected": np.array([np.nan, 0, -5, -5, 0]),
    },
    {  # Test whether exceeding the max deviations gives average deviation equal to 0.
        "observed_elevations": np.array([10, 10, 10, 10, 10]),
        "rule_curve": np.array([20, 20, 20, 20, 20]),
        "periods": 2,
        "inflows": np.array([10, 10, 10, 10, 10]),
        "qin_max": np.inf,
        "maximum_difference": 1,
        "expected": np.array([np.nan, 0, 0, 0, 0]),
    },
    {  # Test the number of periods equal to the array length.
        "observed_elevations": np.array([10, 10, 10, 10, 10]),
        "rule_curve": np.array([10, 10, 10, 10, 20]),
        "periods": 5,
        "inflows": np.array([10, 10, 10, 10, 10]),
        "qin_max": np.inf,
        "maximum_difference": np.inf,
        "expected": np.array([np.nan, np.nan, np.nan, np.nan, -2]),
    },
]


@pytest.mark.parametrize("test_case", test_data)
def test_rule_curve_deviation(test_case):
    """Test different input cases for the rule_curve_deviation function."""
    expected = test_case.pop("expected")
    result = rule_curve_deviation(**test_case)
    assert len(expected) == len(result), "List of average deviations is of incorrect length."
    np.testing.assert_array_equal(expected, result)


@pytest.mark.parametrize(
    "observed_elevations, rule_curve, periods, expected_error",
    [
        # Pool elevations and rule curve have different lengths.
        (np.array([1, 2, 3]), np.array([1, 2]), 2, ValueError),
        # Pool elevation contains NaN values.
        (np.array([1, 2, np.nan]), np.array([1, 2, 3]), 2, ValueError),
        # Periods less than 1.
        (np.array([1, 2, 3]), np.array([1, 2, 3]), 0, ValueError),
        # Periods greater than number of observed elevations.
        (np.array([1, 2, 3]), np.array([1, 2, 3]), 4, ValueError),
    ],
)
def test_rule_curve_deviation_exceptions(observed_elevations, rule_curve, periods, expected_error):
    """Test whether the ruladj functions raises exceptions when expected."""
    with pytest.raises(expected_error):
        rule_curve_deviation(observed_elevations, rule_curve, periods, np.array([0, 0, 0]))
