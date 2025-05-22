"""Module for testing lookup-table functionalities."""
import re
from pathlib import Path
from typing import Iterable, List

import casadi as ca
import numpy.testing
import pytest

import rtctools_simulation.lookup_table as lut

DATA_DIR = Path(__file__).parent.resolve() / "lookup_tables"


def contains_regex(regex: re.Pattern, messages: List[str]):
    """
    Check that a list of messages contains a given regex

    :param regex: a regular expression
    :param messages: a list of strings
    :returns: True if any of the messages contains the given regex.
    """
    for message in messages:
        if re.search(regex, message):
            return True
    return False


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


def test_get_lookup_tables_bounds_from_csv():
    """Test getting a dict of lookup tables bounds described by a csv file."""
    bounds = lut.get_lookup_tables_bounds_from_csv(DATA_DIR / "lookup_tables.csv")
    v_min = bounds["h_from_v"]["v"][0]
    v_max = bounds["h_from_v"]["v"][1]
    h_min = bounds["h_from_v"]["h"][0]
    h_max = bounds["h_from_v"]["h"][1]
    numpy.testing.assert_almost_equal(v_min, 0.0)
    numpy.testing.assert_almost_equal(v_max, 2.0)
    numpy.testing.assert_almost_equal(h_min, 0.0)
    numpy.testing.assert_almost_equal(h_max, 1.5)


@pytest.mark.parametrize(
    "var_in,var_out,values_in,value_out",
    [
        ("h", "v", [0.5], 0.0),
        (["day", "h"], "qout", [1, 0.6], 0.0),
    ],
)
def test_get_empty_lookup_table(var_in, var_out, values_in, value_out):
    """Test getting an empty lookup table."""
    lookup_table = lut.get_empty_lookup_table(
        name="lookup_table",
        var_in=var_in,
        var_out=var_out,
    )
    numpy.testing.assert_almost_equal(lookup_table(*values_in), value_out)


def get_mx_symbols(vars: Iterable[str]):
    """Get a dict of ca.MX symbols."""
    return {var: ca.MX.sym(var) for var in vars}


def test_get_lookup_table_equations_from_csv():
    """Test getting lookup-table equations described by a csv file."""
    values = {
        "Day": 2,
        "V": 1.4,
        "H": 1.2,
        "H2": 0,
        "QSpill": 0.2,
        "QOut": 0.15,
    }
    variables = get_mx_symbols(values.keys())
    lookup_tables = lut.get_lookup_tables_from_csv(DATA_DIR / "lookup_tables.csv")
    equations = lut.get_lookup_table_equations_from_csv(
        file=DATA_DIR / "lookup_table_equations.csv",
        lookup_tables=lookup_tables,
        variables=variables,
        allow_missing_lookup_tables=True,
    )
    residual_fun = ca.Function(
        "residual",
        variables.values(),
        equations,
        variables.keys(),
        ["ResH", "ResH2", "ResQSpill", "ResQOut"],
    )
    resdiual = residual_fun(**values)
    numpy.testing.assert_almost_equal(resdiual["ResH"], 0)
    numpy.testing.assert_almost_equal(resdiual["ResH2"], 0)
    numpy.testing.assert_almost_equal(resdiual["ResQSpill"], 0)
    numpy.testing.assert_almost_equal(resdiual["ResQOut"], 0)


def test_get_lookup_table_equations_check():
    """Test lookup table check when getting lookup table equations."""
    variables = get_mx_symbols(["H", "QOut"])
    lookup_tables = lut.get_lookup_tables_from_csv(DATA_DIR / "lookup_tables.csv")
    exception_pattern = "Lookup table qout_from_day_h has wrong number of inputs"
    with pytest.raises(AssertionError) as e_info:
        lut.get_lookup_table_equations_from_csv(
            file=DATA_DIR / "lookup_table_equations_bad.csv",
            lookup_tables=lookup_tables,
            variables=variables,
        )
    assert contains_regex(exception_pattern, e_info.value.args)
