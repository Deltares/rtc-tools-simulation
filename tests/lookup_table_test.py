"""Module for testing lookup-table functionalities."""
from pathlib import Path

import casadi as ca
import numpy.testing
import pytest
import rtctools_simulation.lookup_table as lut

DATA_DIR = Path(__file__).parent.resolve() / "lookup_tables"


@pytest.mark.parametrize(
    "file,var_in,var_out,values_in,value_out",
    [
        ("h_from_v.csv", "h", "v", [0.5], 0.5),
        ("h_from_v.csv", "h", "v", [1.1], 1.2),
        ("h_from_v.csv", "h", "v", [2.0], 3.0),
        ("qout_from_day_h.csv", ["day", "h"], "qout", [1, 0.6], 0.0),
        ("qout_from_day_h.csv", ["day", "h"], "qout", [1, 1.2], 0.2),
        ("qout_from_day_h.csv", ["day", "h"], "qout", [2, 0.6], 0.0),
        ("qout_from_day_h.csv", ["day", "h"], "qout", [2, 1.2], 0.15),
        ("qout_from_single_day_h.csv", ["day", "h"], "qout", [2, 1.2], 0.2),
    ],
)
def test_get_lookup_table_from_csv(file, var_in, var_out, values_in, value_out):
    """Test getting a lookup table from a csv file."""
    lookup_table = lut.get_lookup_table_from_csv(
        name="lookup_table",
        file=DATA_DIR / file,
        var_in=var_in,
        var_out=var_out,
    )
    numpy.testing.assert_almost_equal(lookup_table(*values_in), value_out)


def test_check_input_grid():
    """Test checking the input grid for a 2D lookup table."""
    with pytest.raises(lut.GridCoordinatesNotFoundError):
        lut.get_lookup_table_from_csv(
            name="bad_input_grid",
            file=DATA_DIR / "bad_input_grid.csv",
            var_in=["day", "h"],
            var_out="qout",
        )


def test_get_lookup_tables_from_csv():
    """Test getting a dict of lookup tables described by a csv file."""
    lookup_tables = lut.get_lookup_tables_from_csv(DATA_DIR / "lookup_tables.csv")
    h_from_v = lookup_tables["h_from_v"]
    qspill_from_h = lookup_tables["qspill_from_h"]
    qout_from_day_h = lookup_tables["qout_from_day_h"]
    numpy.testing.assert_almost_equal(h_from_v(1.2), 1.1)
    numpy.testing.assert_almost_equal(qspill_from_h(1.1), 0.1)
    numpy.testing.assert_almost_equal(qout_from_day_h(2, 1.5), 0.375)


def test_get_lookup_table_equations_from_csv():
    """Test getting lookup-table equations described by a csv file."""
    variables = {
        "Day": ca.MX.sym("Day"),
        "V": ca.MX.sym("V"),
        "H": ca.MX.sym("H"),
        "QSpill": ca.MX.sym("QSpill"),
        "QOut": ca.MX.sym("QOut"),
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
        ["ResH", "ResQSpill", "ResQOut"],
    )
    day = 2
    volume = 1.4
    height = 1.2
    q_spill = 0.2
    q_out = 0.15
    resdiual = residual_fun(V=volume, H=height, QSpill=q_spill, QOut=q_out, Day=day)
    numpy.testing.assert_almost_equal(resdiual["ResH"], 0)
    numpy.testing.assert_almost_equal(resdiual["ResQSpill"], 0)
    numpy.testing.assert_almost_equal(resdiual["ResQOut"], 0)
