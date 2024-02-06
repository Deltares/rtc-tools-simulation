"""Module for testing the spillway model"""
from pathlib import Path

import numpy as np
import numpy.testing
import pandas as pd
from rtctools.simulation.csv_mixin import CSVMixin
from rtctools.simulation.simulation_problem import SimulationProblem

import rtctools_simulation_modelling_extension.lookup_table as lut

SPILLWAY_DIR = Path(__file__).parent.resolve() / "spillway_model"


class SpillwayModel(CSVMixin, SimulationProblem):
    """Class for simulating a spillway model."""

    def __init__(self):
        super().__init__(
            input_folder=SPILLWAY_DIR / "input",
            output_folder=SPILLWAY_DIR / "output",
            model_folder=SPILLWAY_DIR / "model",
            model_name="Spillway",
        )

    def extra_equations(self):
        """Add equations that involve lookuptables."""
        variables = self.get_variables()
        lookup_tables_csv = SPILLWAY_DIR / "lookup_tables" / "lookup_tables.csv"
        lookup_tables = lut.get_lookup_tables_from_csv(lookup_tables_csv)
        equations = lut.get_lookup_table_equations_from_csv(
            file=SPILLWAY_DIR / "model" / "lookup_table_equations.csv",
            lookup_tables=lookup_tables,
            variables=variables,
        )
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
