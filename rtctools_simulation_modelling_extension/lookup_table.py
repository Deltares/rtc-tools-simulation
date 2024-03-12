"""Module for adding lookup tables to a model."""
from pathlib import Path
from typing import Dict, List

import casadi as ca
import pandas as pd


def get_lookup_table_from_csv(
    name: str,
    file: Path,
    var_in: str,
    var_out: str,
) -> ca.Function:
    """
    Get a lookup table from a csv file.

    :name: name of the lookup table
    :param file: CSV file containing data points for different variables.
    :var_in: Input variable of the lookup table. Should be one of the CSV file columns.
    :var_out: Output variable of the lookup table. Should be one of the CSV file columns.

    :return: lookup table in the form of a Casadi function.
    """
    data_csv = Path(file)
    assert data_csv.is_file()
    df = pd.read_csv(data_csv, sep=",")
    lookup_table = ca.interpolant(name, "linear", [df[var_in]], df[var_out])
    return lookup_table


def get_lookup_tables_from_csv(
    file: Path,
    data_dir: Path = None,
) -> Dict[str, ca.Function]:
    """
    Get a dict of lookup tables described by a csv file.

    :param file: CSV File that describes lookup tables.
        The names of the columns correspond to the parameters of :func:`get_lookup_table`.
    :param data_dir: Directory that contains the interpolation data for the lookup tables.
        By default, the directory of the csv file is used.

    :return: dict of lookup tables.
    """
    lookup_tables = {}
    lookup_tables_csv = Path(file)
    assert lookup_tables_csv.is_file()
    if data_dir is None:
        data_dir = lookup_tables_csv.parent
    else:
        data_dir = Path(data_dir)
        assert data_dir.is_dir()
    lookup_tables_df = pd.read_csv(lookup_tables_csv, sep=",")
    for _, lookup_table_df in lookup_tables_df.iterrows():
        name = lookup_table_df["name"]
        data_csv = Path(data_dir / lookup_table_df["data"])
        lookup_tables[name] = get_lookup_table_from_csv(
            name=name,
            file=data_csv,
            var_in=lookup_table_df["var_in"],
            var_out=lookup_table_df["var_out"],
        )
    return lookup_tables


def get_lookup_table_equations_from_csv(
    file: Path, lookup_tables: Dict[str, ca.Function], variables: Dict[str, ca.MX]
) -> List[ca.MX]:
    """
    Get a list of lookup-table equations described by a csv file.

    :param file:
        CSV File that describes equations involving lookup tables.
        These equations are of the form :math:`var_out = lookup_table(var_in)`
        The csv file consists of the following columns:
        * lookup_table: Name of the lookup table.
        * var_in: Input variable of the lookup table. Should be defined in the model.
        * var_out: Output variable of the lookup table. Should be defined in the model.
    :param lookup_tables: Dict of lookup tables.
    :param variables: Dict of symbolic variables used in the model.

    :return: list of equations.
    """
    equations = []
    equations_csv = Path(file)
    assert equations_csv.is_file()
    equations_df = pd.read_csv(equations_csv, sep=",")
    for _, equation_df in equations_df.iterrows():
        lookup_table = lookup_tables[equation_df["lookup_table"]]
        var_in = variables[equation_df["var_in"]]
        var_out = variables[equation_df["var_out"]]
        equations.append(lookup_table(var_in) - var_out)
    return equations
