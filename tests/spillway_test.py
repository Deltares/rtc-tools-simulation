"""Module for testing the spillway model"""
from pathlib import Path

import numpy as np
import numpy.testing
import pandas as pd

import rtctools_simulation_modelling_extension.lookup_table as lut
from rtctools_simulation_modelling_extension.model import Model
from rtctools_simulation_modelling_extension.model_config import ModelConfig

SPILLWAY_DIR = Path(__file__).parent.resolve() / "spillway_model"


class SpillwayModel(Model):
    """Class for simulating a spillway model."""

    config = ModelConfig(
        model="Spillway",
        base_dir=SPILLWAY_DIR,
    )

    def extra_equations(self):
        """Add equations that involve lookuptables."""
        equations = lut.get_lookup_table_equations_from_model(self)
        return equations

    def output_df(self):
        """Return the output in the form of a dataframe."""
        output_file = SPILLWAY_DIR / "output" / "timeseries_export.csv"
        output_df = pd.read_csv(output_file, sep=",")
        return output_df


def test_spillway():
    """Test the spillway model."""
    problem = SpillwayModel()
    problem.simulate()
    output = problem.output_df()
    v = np.array(output["V"])
    v_ref = np.array([1.3, 0.8, 1.2])
    numpy.testing.assert_array_almost_equal(v, v_ref, decimal=3)
