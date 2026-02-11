"""Tests for apply_rulecurve enforce_qmin and get_feasible_qmin integration."""

from pathlib import Path

import pytest

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"
OUTPUT_DIR = BASE_DIR / "output_feasible_qmin"
TOLERANCE = 1e-6  # Numerical tolerance for float comparisons


class RuleCurveWithQminModel(ReservoirModel):
    """Model that uses apply_rulecurve with enforce_qmin=True."""

    def __init__(self, config, qmin_params=None, **kwargs):
        super().__init__(config, **kwargs)
        self.qmin_params = qmin_params or {}

    def parameters(self):
        params = super().parameters()
        params.update(self.qmin_params)
        return params

    def apply_schemes(self):
        self.apply_rulecurve(enforce_qmin=True)


def test_qmin_enforced_in_output():
    """Test that Q_out in model output respects the enforced Qmin.

    Scenario:
    - Initial H = 1.15, rule curve target = 0.9
    - Rule curve would compute discharge ~ 0.4 m3/s to reach target
    - Qmin = 0.5 m3/s (higher than rule curve discharge)
    - Reservoir_Hdead = 0.0, Reservoir_Hbuffer = 0.1 (H > Hbuffer, so full Qmin applies)
    - Expected: Q_out >= Qmin at timestep 1
    """
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    qmin_params = {
        "Reservoir_Qmin": 0.5,
        "Reservoir_Hdead": 0.0,
        "Reservoir_Hbuffer": 0.1,
    }

    model = RuleCurveWithQminModel(config, qmin_params=qmin_params)
    model.simulate()

    output = model.extract_results()
    q_out = output["Q_out"]

    # Rule curve discharge ~ 0.4 < Qmin = 0.5, so Qmin is enforced
    assert (
        q_out[1] >= qmin_params["Reservoir_Qmin"] - TOLERANCE
    ), f"Q_out at timestep 1 is {q_out[1]}, expected >= {qmin_params['Reservoir_Qmin']}"


def test_qmin_reduced_when_reservoir_low():
    """Test that feasible Qmin is reduced when reservoir level approaches dead storage.

    Scenario:
    - Set Qmin = 1.0 m3/s
    - Set Reservoir_Hdead = 0.0, Reservoir_Hbuffer = 1.0
    - Initial H = 1.15 (above buffer, so full Qmin applies at step 1)
    - After step 1, H drops below Hbuffer due to enforcing Qmin=1.0
    - At step 2, feasible Qmin should be reduced (linear interpolation)
    """
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    qmin_params = {
        "Reservoir_Qmin": 1.0,
        "Reservoir_Hdead": 0.0,
        "Reservoir_Hbuffer": 1.0,
    }

    model = RuleCurveWithQminModel(config, qmin_params=qmin_params)
    model.simulate()

    output = model.extract_results()
    q_out = output["Q_out"]
    h_out = output["H"]

    # At step 1: H=1.15 > Hbuffer=1.0, so full Qmin=1.0 applies
    assert q_out[1] >= qmin_params["Reservoir_Qmin"] - TOLERANCE, (
        f"Expected Q_out >= {qmin_params['Reservoir_Qmin']} at step 1 (H > Hbuffer), "
        f"got {q_out[1]}"
    )

    # At step 2: H dropped below Hbuffer, so Qmin should be reduced
    assert q_out[2] < qmin_params["Reservoir_Qmin"] - TOLERANCE, (
        f"Expected reduced Q_out at step 2 (H < Hbuffer), "
        f"got {q_out[2]} (should be < {qmin_params['Reservoir_Qmin']})"
    )
    # Still releases water (H is well above Hdead)
    assert q_out[2] > 0, f"Expected positive Q_out at step 2, got {q_out[2]}"
    # Reservoir doesn't drain below dead storage
    assert (
        h_out[2] >= qmin_params["Reservoir_Hdead"]
    ), f"H should not drop below dead storage, got {h_out[2]}"


def test_feasible_qmin_respects_physical_constraint():
    """Test that enforce_qmin caps discharge by physical constraint.

    Scenario:
    - Set very high Qmin (10.0 m3/s) that would drain reservoir instantly
    - Set Reservoir_Hdead close to initial level (1.0, initial H=1.15)
    - Rule curve discharge ~ 0.4 < Qmin, so Qmin enforcement is triggered
    - Expected: Q_out is capped by physical constraint, NOT the full Reservoir_Qmin

    This verifies that when Qmin enforcement is triggered, the applied value
    is bounded by what's physically available above dead storage.
    """
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    qmin_params = {
        "Reservoir_Qmin": 10.0,  # Very high - would drain reservoir instantly
        "Reservoir_Hdead": 1.0,  # Close to initial H=1.15
        "Reservoir_Hbuffer": 1.1,  # Buffer just above dead
    }

    model = RuleCurveWithQminModel(config, qmin_params=qmin_params)
    model.simulate()

    output = model.extract_results()
    q_out = output["Q_out"]

    # At step 1: Rule curve discharge ~ 0.4 < policy Qmin = 10.0
    # But physical constraint limits release to what's available above V_dead
    # The applied Q_out should be much less than Reservoir_Qmin
    assert q_out[1] < qmin_params["Reservoir_Qmin"], (
        f"Expected Q_out ({q_out[1]}) < Reservoir_Qmin ({qmin_params['Reservoir_Qmin']}). "
        f"Physical constraint should cap the feasible Qmin."
    )

    # The applied Q_out should be positive (there is some water above dead storage)
    assert q_out[1] > 0, f"Expected positive Q_out at step 1, got {q_out[1]}"


def test_enforce_qmin_false_is_default():
    """Test that enforce_qmin=False (default) does not modify discharge."""
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    qmin_params = {
        "Reservoir_Qmin": 0.5,  # Higher than rule curve discharge (0.4)
        "Reservoir_Hdead": 0.0,
        "Reservoir_Hbuffer": 0.1,
    }

    class NoQminModel(ReservoirModel):
        def parameters(self):
            params = super().parameters()
            params.update(qmin_params)
            return params

        def apply_schemes(self):
            self.apply_rulecurve()  # default: enforce_qmin=False

    model = NoQminModel(config)
    model.simulate()
    output = model.extract_results()
    q_out = output["Q_out"]

    # Without enforce_qmin, Q_out should match rule curve discharge
    # and not apply Reservoir_Qmin
    # Rule curve discharge calculation: Q = (V_current - V_target) / blend
    # H_current=1.15 → V=1.3, H_target=0.9 → V=0.9, blend=1
    # Q = (1.3 - 0.9) / 1 = 0.4 m³/s
    rule_curve_discharge = 0.4
    assert (
        abs(q_out[1] - rule_curve_discharge) < TOLERANCE
    ), f"Expected rule curve discharge {rule_curve_discharge}, got {q_out[1]}"

    # And it should NOT be boosted to Reservoir_Qmin
    assert q_out[1] < qmin_params["Reservoir_Qmin"], (
        f"Without enforce_qmin, Q_out should not reach Qmin. "
        f"Got Q_out={q_out[1]}, Qmin={qmin_params['Reservoir_Qmin']}"
    )


def test_get_feasible_qmin_standalone():
    """Test that get_feasible_qmin remains callable as standalone utility."""
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    qmin_params = {
        "Reservoir_Qmin": 0.5,
        "Reservoir_Hdead": 0.0,
        "Reservoir_Hbuffer": 0.1,
    }

    class StandaloneQminModel(ReservoirModel):
        def __init__(self, config, **kwargs):
            super().__init__(config, **kwargs)
            self.qmin_values = []

        def parameters(self):
            params = super().parameters()
            params.update(qmin_params)
            return params

        def apply_schemes(self):
            self.apply_rulecurve()
            if self.get_current_time() != self.get_start_time():
                self.qmin_values.append(self.get_feasible_qmin())

    model = StandaloneQminModel(config)
    model.simulate()

    assert len(model.qmin_values) > 0
    for val in model.qmin_values:
        assert isinstance(val, float)
        assert val >= 0


def test_missing_reservoir_qmin_raises_error():
    """Test that enforce_qmin=True without Reservoir_Qmin raises ValueError.

    Verifies:
    - ValueError is raised with informative message
    - Error message includes Reservoir_Qmin parameter name
    - Error message includes the calling function name for context
    """
    config = ModelConfig(base_dir=BASE_DIR, dirs={"output": OUTPUT_DIR})

    class MissingQminModel(ReservoirModel):
        def apply_schemes(self):
            self.apply_rulecurve(enforce_qmin=True)

    model = MissingQminModel(config)

    with pytest.raises(ValueError) as exc_info:
        model.simulate()

    error_message = str(exc_info.value)
    assert "Reservoir_Qmin" in error_message
    assert "not configured" in error_message
    assert "apply_rulecurve" in error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
