"""Module for testing lookup-table functionalities."""
from pathlib import Path

import casadi as ca
import numpy.testing

import rtctools_simulation_modelling_extension.lookup_table as lut

DATA_DIR = Path(__file__).parent.resolve() / "lookup_tables"


def test_get_lookup_table_from_csv():
    """Test getting a lookup table from a csv file."""
    v_from_h = lut.get_lookup_table_from_csv(
        name="v_from_h",
        file=DATA_DIR / "h_from_v.csv",
        var_in="h",
        var_out="v",
    )
    numpy.testing.assert_almost_equal(v_from_h(0.5), 0.5)
    numpy.testing.assert_almost_equal(v_from_h(1.1), 1.2)
    numpy.testing.assert_almost_equal(v_from_h(2.0), 3.0)


def test_get_lookup_tables_from_csv():
    """Test getting a dict of lookup tables described by a csv file."""
    lookup_tables = lut.get_lookup_tables_from_csv(DATA_DIR / "lookup_tables.csv")
    h_from_v = lookup_tables["h_from_v"]
    qspill_from_h = lookup_tables["qspill_from_h"]
    numpy.testing.assert_almost_equal(h_from_v(1.2), 1.1)
    numpy.testing.assert_almost_equal(qspill_from_h(1.1), 0.1)


def test_get_lookup_table_equations_from_csv():
    """Test getting lookup-table equations described by a csv file."""
    variables = {
        "V": ca.MX.sym("V"),
        "H": ca.MX.sym("H"),
        "QSpill": ca.MX.sym("QSpill"),
    }
    lookup_tables = lut.get_lookup_tables_from_csv(DATA_DIR / "lookup_tables.csv")
    equations = lut.get_lookup_table_equations_from_csv(
        file=DATA_DIR / "lookup_table_equations.csv",
        lookup_tables=lookup_tables,
        variables=variables,
    )
    residual_fun = ca.Function(
        "residual",
        variables.values(),
        equations,
        variables.keys(),
        ["ResH", "ResQSpill"],
    )
    v_in = 1.2
    h_in = 1.3
    q_spill_in = 0.4
    h_out = lookup_tables["h_from_v"](v_in)
    q_spill_out = lookup_tables["qspill_from_h"](h_in)
    resdiual = residual_fun(V=v_in, H=h_in, QSpill=q_spill_in)
    numpy.testing.assert_almost_equal(resdiual["ResH"], h_out - h_in)
    numpy.testing.assert_almost_equal(resdiual["ResQSpill"], q_spill_out - q_spill_in)
