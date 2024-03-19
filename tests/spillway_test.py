"""Module for testing the spillway model"""
from pathlib import Path

import numpy as np
import numpy.testing
import pandas as pd

from rtctools_simulation_modelling_extension.reservoir.model import ModelConfig, ReservoirModel

SPILLWAY_DIR = Path(__file__).parent.resolve() / "spillway_model"


class SpillwayModel(ReservoirModel):
    """Class for simulating a spillway model."""

    def apply_schemes(self):
        """Always apply spillway."""
        self.apply_spillway()

    def output_df(self):
        """Return the output in the form of a dataframe."""
        output_file = SPILLWAY_DIR / "output" / "timeseries_export.csv"
        output_df = pd.read_csv(output_file, sep=",")
        return output_df


def test_spillway():
    """Test the spillway model."""
    config = ModelConfig(base_dir=SPILLWAY_DIR)
    model = SpillwayModel(config)
    model.simulate()
    output = model.output_df()
    v = np.array(output["V"])
    v_ref = np.array([1.3, 0.8, 1.2])
    numpy.testing.assert_array_almost_equal(v, v_ref, decimal=3)
