"""Tests for rule curve functions."""

import datetime
from pathlib import Path

import numpy as np
import pytest

from rtctools_simulation.model_config import ModelConfig
from rtctools_simulation.reservoir.model import ReservoirModel
from rtctools_simulation.reservoir.rule_curve import rule_curve_deviation, rule_curve_discharge

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"
OUTPUT_DIR = BASE_DIR / "output_rule_curve"


class RuleCurveModel(ReservoirModel):
    """Class for simulating a rule curve model."""

    def __init__(self, config, do_apply_rulecurve=True, **kwargs):
        super().__init__(config, **kwargs)
        self.do_apply_rulecurve = do_apply_rulecurve

    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)
        self.calculate_rule_curve_deviation(periods=1)
        t_0 = datetime.datetime(2020, 1, 1, 0, second=1)
        self.adjust_rulecurve(periods=1, extrapolate_trend_linear=True, application_time=t_0)

    def apply_schemes(self):
        """Apply rule curve."""
        if self.do_apply_rulecurve:
            self.apply_rulecurve()


@pytest.mark.parametrize(
    "target_volume, current_volume, q_max, blend, expected",
    [
        (5, 10, np.inf, 1, 5),  # Test positive inflow with one timestep.
        (10, 5, np.inf, 1, 0),  # Test zero outflow when target is higher than current.
        (5, 10, np.inf, 2, 2.5),  # Test positive flow in with two timesteps.
        (5, 10, 1, 2, 1),  # Test limiting q_max.
    ],
)
def test_rule_curve(target_volume, current_volume, q_max, blend, expected):
    result = rule_curve_discharge(target_volume, current_volume, q_max, blend)
    assert expected == result, f"Expected outflow: {expected}, got: {result}"


@pytest.mark.parametrize(
    "do_apply_rulecurve, q_ref, v_ref, h_ref, rulecurve_ref",
    [
        (
            True,  # blend=1, q_max=10, rule_curve is 0.5 for each step.
            np.array([0.8, 0.8, 0.0]),
            np.array([1.3, 0.5, 1.5]),
            np.array([1.15, 0.5, 1.25]),
            np.array([0.8, 0.8, 0.8]),
        ),
        (
            False,
            np.array([0.0, 0.5, 0.5]),
            np.array([1.3, 0.8, 1.3]),
            np.array([1.15, 0.8, 1.15]),
            np.array([0.5, 0.5, 0.5]),
        ),
    ],
)
def test_rule_curve_scheme(do_apply_rulecurve, q_ref, v_ref, h_ref, rulecurve_ref):
    """Test the rule curve scheme."""
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})
    model = RuleCurveModel(config, do_apply_rulecurve=do_apply_rulecurve)
    model.simulate()
    output = model.extract_results()
    print(output)
    q_out = np.array(output["Q_out"])
    v_out = np.array(output["V"])
    h_out = np.array(output["H"])
    new_rulecurve = model.io.get_timeseries("rule_curve")[1]
    np.testing.assert_array_almost_equal(q_out, q_ref, decimal=3)
    np.testing.assert_array_almost_equal(v_out, v_ref, decimal=3)
    np.testing.assert_array_almost_equal(h_out, h_ref, decimal=3)
    np.testing.assert_array_almost_equal(new_rulecurve, rulecurve_ref, decimal=3)


@pytest.mark.parametrize(
    "observed_elevations, rule_curve, periods, inflows, qin_max,"
    " maximum_difference, expected_outcome",
    [
        (  ## Check deviation first timestep
            np.array([0.5, np.nan, np.nan]),
            np.array([1, 1, 1]),
            1,
            None,
            np.inf,
            np.inf,
            np.array([-0.5, 0, 0]),
        ),
        (  ## Check deviation averaging, looking periods amount of timesteps backwards
            np.array([0.5, 0.7, np.nan]),
            np.array([1, 1, 1]),
            2,
            None,
            np.inf,
            np.inf,
            np.array([np.nan, -0.4, -0.3]),
        ),
        (  ## exceeding max_diff sets deviation to 0
            np.array([0.5, 0.7, np.nan]),
            np.array([1, 1, 1]),
            1,
            None,
            np.inf,
            0.4,
            np.array([0, -0.3, 0]),
        ),
        (  ## more than 50% NaNs in period defaults to 0
            np.array([0.6, 0.7, 0.7, np.nan, np.nan, np.nan, np.nan, 0.8, np.nan]),
            np.array([1, 1, 1, 1, 1, 1, 1, 1, 1]),
            4,
            None,
            np.inf,
            0.4,
            np.array([np.nan, np.nan, np.nan, -0.333, -0.3, 0, 0, 0, 0]),
        ),
    ],
)
def test_rule_curve_deviation(
    observed_elevations, rule_curve, periods, inflows, qin_max, maximum_difference, expected_outcome
):
    """Test the rule curve deviation scheme."""
    outcome = rule_curve_deviation(
        observed_elevations, rule_curve, periods, inflows, qin_max, maximum_difference
    )
    print(outcome)
    np.testing.assert_array_almost_equal(outcome, expected_outcome, decimal=3)


if __name__ == "__main__":
    pytest.main()
