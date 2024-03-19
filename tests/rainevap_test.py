"""Module for testing the rainevap scheme."""
from pathlib import Path

import numpy as np
import numpy.testing
import pytest

from rtctools_simulation_modelling_extension.reservoir.model import ModelConfig, ReservoirModel

SPILLWAY_DIR = Path(__file__).parent.resolve() / "spillway_model"
OUTPUT_DIR = SPILLWAY_DIR / "output_rainevap"


class RainevapModel(ReservoirModel):
    """Class for simulating a rainevap model."""

    def __init__(self, config, do_include_rainevap=True, **kwargs):
        super().__init__(config, **kwargs)
        self.do_include_rainevap = do_include_rainevap

    def apply_schemes(self):
        """Apply rainevap."""
        if self.do_include_rainevap:
            self.include_rainevap()


@pytest.mark.parametrize(
    "do_include_rainevap, q_ref, v_ref, q_rain_ref, q_evap_ref",
    [
        (
            True,
            np.array([0.0, 0.5, 0.5]),
            np.array([1.3, 8.951, 9.448]),
            np.array([0, 8.151, 0]),
            np.array([0, 0, 0.003]),
        ),
        (
            False,
            np.array([0.0, 0.5, 0.5]),
            np.array([1.3, 0.8, 1.3]),
            np.array([0, 0, 0]),
            np.array([0, 0, 0]),
        ),
    ],
)
def test_rainevap(do_include_rainevap, q_ref, v_ref, q_rain_ref, q_evap_ref):
    """Test the rainevap model."""
    config = ModelConfig(base_dir=SPILLWAY_DIR, dirs={"output": OUTPUT_DIR})
    model = RainevapModel(config, do_include_rainevap=do_include_rainevap)
    model.simulate()
    output = model.extract_results()
    q_out = np.array(output["Q_out"])
    v_out = np.array(output["V"])
    q_rain = np.array(output["Q_rain"])
    q_evap = np.array(output["Q_evap"])
    numpy.testing.assert_array_almost_equal(q_out, q_ref, decimal=3)
    numpy.testing.assert_array_almost_equal(v_out, v_ref, decimal=3)
    numpy.testing.assert_array_almost_equal(q_rain, q_rain_ref, decimal=3)
    numpy.testing.assert_array_almost_equal(q_evap, q_evap_ref, decimal=3)
