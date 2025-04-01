"""Tests for rule curve functions."""

from pathlib import Path

import numpy as np
import pytest

from rtctools_simulation.model_config import ModelConfig
from rtctools_simulation.reservoir.model import ReservoirModel
from rtctools_simulation.reservoir.rule_curve import (
    rule_curve_discharge,
)

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"
OUTPUT_DIR = BASE_DIR / "output_rule_curve"


class RuleCurveModel(ReservoirModel):
    """Class for simulating a rule curve model."""

    def __init__(self, config, do_apply_rulecurve=True, **kwargs):
        super().__init__(config, **kwargs)
        self.do_apply_rulecurve = do_apply_rulecurve
        self.calculate_rule_curve_deviation(periods=1)
        self.adjust_rulecurve(periods=1, extrapolate_trend_linear=True)

    def apply_schemes(self):
        """Apply rule curve."""
        if self.do_apply_rulecurve:
            self.apply_rulecurve()


@pytest.mark.parametrize(
    "target_volume, current_volume, q_max, blend, expected",
    [
        (5, 10, np.inf, 1, 5),  # Test postive flow in with one timestep.
        (10, 5, np.inf, 1, 0),  # Test zero outflow when target is higher than current.
        (5, 10, np.inf, 2, 2.5),  # Test positive flow in with two timesteps.
        (5, 10, 1, 2, 1),  # Test limiting q_max.
    ],
)
def test_rule_curve(target_volume, current_volume, q_max, blend, expected):
    result = rule_curve_discharge(target_volume, current_volume, q_max, blend)
    assert expected == result, f"Expected outflow: {expected}, got: {result}"


@pytest.mark.parametrize(
    "do_apply_rulecurve, q_ref, v_ref, h_ref",
    [
        (
            True,  # blend=1, q_max=10, rule_curve is 0.5 for each step.
            np.array([0.8, 0.8, 0.0]),
            np.array([1.3, 0.5, 1.5]),
            np.array([1.15, 0.5, 1.25]),
        ),
        (
            False,
            np.array([0.0, 0.5, 0.5]),
            np.array([1.3, 0.8, 1.3]),
            np.array([1.15, 0.8, 1.15]),
        ),
    ],
)
def test_rule_curve_scheme(do_apply_rulecurve, q_ref, v_ref, h_ref):
    """Test the rule curve scheme."""
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})
    model = RuleCurveModel(config, do_apply_rulecurve=do_apply_rulecurve)
    model.simulate()
    output = model.extract_results()
    q_out = np.array(output["Q_out"])
    v_out = np.array(output["V"])
    h_out = np.array(output["H"])
    np.testing.assert_array_almost_equal(q_out, q_ref, decimal=3)
    np.testing.assert_array_almost_equal(v_out, v_ref, decimal=3)
    np.testing.assert_array_almost_equal(h_out, h_ref, decimal=3)


if __name__ == "__main__":
    pytest.main()
