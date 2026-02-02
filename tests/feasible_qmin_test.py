"""Tests for apply_rulecurve return value and get_feasible_qmin integration."""

from pathlib import Path

import pytest

from rtctools_simulation.reservoir._variables import InputVar
from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"
OUTPUT_DIR = BASE_DIR / "output_feasible_qmin"


class RuleCurveWithQminModel(ReservoirModel):
    """Model that uses apply_rulecurve with Qmin enforcement."""

    def __init__(self, config, qmin_params=None, **kwargs):
        super().__init__(config, **kwargs)
        self.qmin_params = qmin_params or {}
        self.rulecurve_returns = []
        self.qmin_applied = []

    def parameters(self):
        params = super().parameters()
        params.update(self.qmin_params)
        return params

    def apply_schemes(self):
        # Capture the return value from apply_rulecurve
        discharge = self.apply_rulecurve()
        self.rulecurve_returns.append(discharge)

        if discharge is None:
            self.qmin_applied.append(None)
            return

        # Use get_feasible_qmin and enforce if needed
        q_min = self.get_feasible_qmin()
        if discharge < q_min:
            self.set_q(
                target_variable=InputVar.Q_TURBINE,
                input_type="parameter",
                input_data=q_min,
            )
            self.qmin_applied.append(q_min)
        else:
            self.qmin_applied.append(discharge)


def test_apply_rulecurve_return_value():
    """Test that apply_rulecurve returns None at t=0 and float after."""
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})
    model = RuleCurveWithQminModel(config)
    model.simulate()

    # At t=0, returns None (discharge given as initial condition)
    assert (
        model.rulecurve_returns[0] is None
    ), f"Expected None at t=0, got {model.rulecurve_returns[0]}"

    # After t=0, returns non-negative float
    for i, value in enumerate(model.rulecurve_returns[1:], start=1):
        assert isinstance(
            value, float
        ), f"Expected float at timestep {i}, got {type(value).__name__}"
        assert value >= 0, f"Expected non-negative at timestep {i}, got {value}"


def test_qmin_enforced_in_output():
    """Test that Q_out in model output respects the enforced Qmin.

    Scenario:
    - Initial H = 1.15, rule curve target = 0.9
    - Rule curve would compute discharge ≈ 0.4 m³/s to reach target
    - Qmin = 0.5 m³/s (higher than rule curve discharge)
    - H_dead = 0.0, H_buffer = 0.1 (H > H_buffer, so full Qmin applies)
    - Expected: Q_out >= Qmin at timestep 1
    """
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    qmin_params = {
        "Reservoir_Qmin": 0.5,
        "H_dead": 0.0,
        "H_buffer": 0.1,
    }

    model = RuleCurveWithQminModel(config, qmin_params=qmin_params)
    model.simulate()

    output = model.extract_results()
    q_out = output["Q_out"]

    # Rule curve discharge ≈ 0.4 < Qmin = 0.5, so Qmin is enforced
    assert (
        q_out[1] >= qmin_params["Reservoir_Qmin"] - 1e-6
    ), f"Q_out at timestep 1 is {q_out[1]}, expected >= {qmin_params['Reservoir_Qmin']}"


def test_qmin_reduced_when_reservoir_low():
    """Test that feasible Qmin is reduced when reservoir level approaches dead storage.

    Scenario:
    - Set Qmin = 1.0 m³/s
    - Set H_dead = 0.0, H_buffer = 1.0
    - Initial H = 1.15 (above buffer, so full Qmin applies at step 1)
    - After step 1, H drops below H_buffer due to enforcing Qmin=1.0
    - At step 2, feasible Qmin should be reduced (linear interpolation)
    """
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    qmin_params = {
        "Reservoir_Qmin": 1.0,
        "H_dead": 0.0,
        "H_buffer": 1.0,
    }

    model = RuleCurveWithQminModel(config, qmin_params=qmin_params)
    model.simulate()

    # At step 1: H=1.15 > H_buffer=1.0, so full Qmin applies
    assert model.qmin_applied[1] == qmin_params["Reservoir_Qmin"], (
        f"Expected Qmin={qmin_params['Reservoir_Qmin']} at step 1 (H > H_buffer), "
        f"got {model.qmin_applied[1]}"
    )

    # At step 2: H dropped below H_buffer, so Qmin should be reduced
    # Verify the reduction actually happened (Qmin < 1.0)
    assert model.qmin_applied[2] is not None, "Expected Qmin at step 2"
    assert model.qmin_applied[2] < qmin_params["Reservoir_Qmin"], (
        f"Expected reduced Qmin at step 2 (H < H_buffer), "
        f"got {model.qmin_applied[2]} (should be < {qmin_params['Reservoir_Qmin']})"
    )


def test_feasible_qmin_respects_physical_constraint():
    """Test that get_feasible_qmin is capped by physical constraint.

    Scenario:
    - Set very high Qmin (10.0 m³/s) that would drain reservoir instantly
    - Set H_dead close to initial level (H_dead=1.0, initial H=1.15)
    - Rule curve discharge ≈ 0.4 < Qmin, so Qmin enforcement is triggered
    - Expected: get_feasible_qmin returns a value capped by physical constraint,
      NOT the full Reservoir_Qmin

    This verifies that when Qmin enforcement is triggered, the applied value
    is bounded by what's physically available above dead storage.
    """
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    qmin_params = {
        "Reservoir_Qmin": 10.0,  # Very high - would drain reservoir instantly
        "H_dead": 1.0,  # Close to initial H=1.15
        "H_buffer": 1.1,  # Buffer just above dead
    }

    model = RuleCurveWithQminModel(config, qmin_params=qmin_params)
    model.simulate()

    # At step 1: Rule curve discharge ≈ 0.4 < policy Qmin = 10.0
    # But physical constraint limits release to what's available above V_dead
    # V_initial ≈ 1.3, V_dead = 1.0, so max release ≈ 0.3 m³/s
    # get_feasible_qmin should return ~0.3, not 10.0

    # The applied Qmin should be much less than Reservoir_Qmin
    applied_qmin = model.qmin_applied[1]
    assert applied_qmin is not None, "Expected Qmin to be applied at step 1"
    q_min_param = qmin_params["Reservoir_Qmin"]
    assert applied_qmin < q_min_param, (
        f"Expected applied Qmin ({applied_qmin}) < Reservoir_Qmin ({q_min_param}). "
        f"Physical constraint should cap the feasible Qmin."
    )

    # The applied Qmin should be positive (there is some water above dead storage)
    assert applied_qmin > 0, f"Expected positive Qmin at step 1, got {applied_qmin}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
