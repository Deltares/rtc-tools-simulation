"""Module for testing lookup-table functionalities."""
import re
from pathlib import Path
from typing import List

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


def get_variables():
    """Get a dict of variables."""
    return {
        "Day": ca.MX.sym("Day"),
        "V": ca.MX.sym("V"),
        "H": ca.MX.sym("H"),
        "QSpill": ca.MX.sym("QSpill"),
        "QOut": ca.MX.sym("QOut"),
    }


def test_get_lookup_table_equations_from_csv():
    """Test getting lookup-table equations described by a csv file."""
    variables = get_variables()
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


def test_get_lookup_table_equations_check():
    """Test lookup table check when getting lookup table equations."""
    variables = get_variables()
    lookup_tables = lut.get_lookup_tables_from_csv(DATA_DIR / "lookup_tables.csv")
    exception_pattern = "Lookup table qout_from_day_h has wrong number of inputs"
    with pytest.raises(AssertionError) as e_info:
        lut.get_lookup_table_equations_from_csv(
            file=DATA_DIR / "lookup_table_equations_bad.csv",
            lookup_tables=lookup_tables,
            variables=variables,
        )
    assert contains_regex(exception_pattern, e_info.value.args)
