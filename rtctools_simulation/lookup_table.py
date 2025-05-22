"""Module for creating lookup tables and lookup table equations."""
from pathlib import Path
from typing import Dict, List, Union

import casadi as ca
import numpy as np
import pandas as pd


class GridCoordinatesNotFoundError(Exception):
    """Error when unable to extract coordinates from a rectangular grid."""

    pass


def _remove_duplicates_from_list(x: list) -> list:
    """
    Remove duplicate values from a list while retaining the original order.
    """
    return list(dict.fromkeys(x))


def _get_coordinates_from_grid(grid: list[list[float]]) -> list[list[float]]:
    """
    Get the coordinate vectors of a given rectangular grid.

    Given a n-dimensional rectangular grid, find the coordinate vectors such that
    ``grid = numpy.meshgrid(*coordinate_vectors)``.
    In other words, this function does the reverse of numpy.meshgrid.
    """
    coordinates = [np.array(co).flatten() for co in grid]
    reduced_coordinates = [_remove_duplicates_from_list(co) for co in grid]
    grid_to_check = np.meshgrid(*reduced_coordinates, indexing="ij")
    coordinates_to_check = [np.array(co).flatten() for co in grid_to_check]
    for co, co_to_check in zip(coordinates, coordinates_to_check):
        if co.shape == co_to_check.shape and np.allclose(co, co_to_check):
            continue
        message = (
            "Could not extract coordinates from grid."
            " Check that the grid is rectangular"
            " and that the first coordinate is the slowest varying coordinate."
        )
        raise GridCoordinatesNotFoundError(message)
    return reduced_coordinates


def _reshape_flattened_array(
    array: list, shape: list[int], initial_ordering: str, new_ordering: str
) -> list:
    """
    Reorder a flattened array.

    Reorder a flattened array by first reshaping it according to a given inital ordering
    and then flattening it again according to a new ordering.
    The ordering parameters can have the same values as the numpy.reshape order parameter.
    """
    np_array = np.array(array)
    reshaped_array = np.reshape(np_array, newshape=shape, order=initial_ordering)
    flat_array = np.ravel(reshaped_array, order=new_ordering)
    return flat_array


def get_lookup_table_data_from_csv(
    file: Path,
    var_in: Union[str, list[str]],
    var_out: str,
):
    """
    Get lookup table data from a csv file. The lookup table is reduced if inputs are constant.

    :param file: CSV file containing data points for different variables.
    :param var_in: Input variable(s) of the lookup table. Should be one of the CSV file columns.
    :param var_out: Output variable of the lookup table. Should be one of the CSV file columns.

    :return: The coordinates and values from the reduced lookup table
    """
    data_csv = Path(file)
    if not data_csv.is_file():
        raise FileNotFoundError(f"File {data_csv} not found.")
    df = pd.read_csv(data_csv, sep=",")
    vars_in: list[str] = var_in if isinstance(var_in, list) else [var_in]
    var_in_grid = [df[var] for var in vars_in]
    try:
        var_in_coordinates = _get_coordinates_from_grid(var_in_grid)
    except GridCoordinatesNotFoundError as error:
        message = (
            f"Grid coordinates for {vars_in} could not be found."
            f" Make sure that the data points of {vars_in} form a rectangular grid"
            f" and that the first input variable"
            f" (in this case '{vars_in[0]}') is the slowest varying one."
        )
        raise GridCoordinatesNotFoundError(message) from error
    reduced_vars_in = [
        var for var, coordinates in zip(vars_in, var_in_coordinates) if len(coordinates) > 1
    ]
    var_in_coordinates = [coords for coords in var_in_coordinates if len(coords) > 1]
    shape = [len(co) for co in var_in_coordinates]
    var_out_values = df[var_out]
    var_out_values = _reshape_flattened_array(
        var_out_values, shape=shape, initial_ordering="C", new_ordering="F"
    )
    return var_in_coordinates, var_out_values, vars_in, reduced_vars_in


def get_lookup_table_bounds_from_csv(
    file: Path, var_in: Union[str, list[str]], var_out: str
) -> Dict:
    """
    Get the bounds from a lookup table csv.

    :param file: CSV file containing data points for different variables.
    :param var_in: Input variable(s) of the lookup table. Should be one of the CSV file columns.
    :param var_out: Output variable of the lookup table. Should be one of the CSV file columns.

    :return: a dictionary containing the min and max values for each input and output variable
        in the lookup table.
    """
    var_in_coordinates, var_out_values, _, reduced_vars_in = get_lookup_table_data_from_csv(
        file, var_in, var_out
    )
    bounds = {}
    for idx, var in enumerate(reduced_vars_in):
        lb = min(var_in_coordinates[idx])
        ub = max(var_in_coordinates[idx])
        bounds[var] = [lb, ub]
    lb = min(var_out_values)
    ub = max(var_out_values)
    bounds[var_out] = [lb, ub]
    return bounds


def get_lookup_tables_bounds_from_csv(
    file: Path,
    data_dir: Path = None,
) -> Dict:
    """
    Get a dict of lookup tables bounds described in a csv file.

    :param file: CSV File that describes lookup tables.
        The column names correspond to the parameters of :func:`get_lookup_table_from_csv`.
        In case of multiple input variables, they should be separated by a whitespace.
    :param data_dir: Directory that contains the interpolation data for the lookup tables.
        By default, the directory of the csv file is used.

    :return: dict of lookup table bounds.
    """
    bounds = extract_from_multiple_csv(
        file=file,
        data_dir=data_dir,
        extraction_type="lookup_tables_bounds",
    )
    return bounds


def get_lookup_table_from_csv(
    name: str,
    file: Path,
    var_in: Union[str, list[str]],
    var_out: str,
) -> ca.Function:
    """
    Get a lookup table from a csv file.

    :param name: name of the lookup table
    :param file: CSV file containing data points for different variables.
    :param var_in: Input variable(s) of the lookup table. Should be one of the CSV file columns.
    :param var_out: Output variable of the lookup table. Should be one of the CSV file columns.

    :return: lookup table in the form of a Casadi function.
    """
    var_in_coordinates, var_out_values, vars_in, reduced_vars_in = get_lookup_table_data_from_csv(
        file, var_in, var_out
    )
    interpolant = ca.interpolant(name, "linear", var_in_coordinates, var_out_values)
    var_in_symbols: list[ca.MX] = [ca.MX.sym(var) for var in vars_in]
    reduced_var_in_symbols = [var for var in var_in_symbols if var.name() in reduced_vars_in]
    reduced_var_in_symbols = ca.vertcat(*reduced_var_in_symbols)
    lookup_table = ca.Function(name, var_in_symbols, [interpolant(reduced_var_in_symbols)])
    return lookup_table


def get_lookup_tables_from_csv(
    file: Path,
    data_dir: Path = None,
) -> Dict[str, ca.Function]:
    """
    Get a dict of lookup tables described by a csv file.

    :param file: CSV File that describes lookup tables.
        The column names correspond to the parameters of :func:`get_lookup_table_from_csv`.
        In case of multiple input variables, they should be separated by a whitespace.
    :param data_dir: Directory that contains the interpolation data for the lookup tables.
        By default, the directory of the csv file is used.

    :return: dict of lookup tables.
    """
    lookup_tables = extract_from_multiple_csv(
        file=file,
        data_dir=data_dir,
        extraction_type="lookup_tables",
    )
    return lookup_tables


def extract_from_multiple_csv(
    file: Path,
    data_dir: Path = None,
    extraction_type="lookup_tables",
) -> Dict:
    """
    Extract a dictionary of information from lookup tables.

    :param file: CSV File that describes lookup tables.
        The column names correspond to the parameters of :func:`get_lookup_table_from_csv`.
        In case of multiple input variables, they should be separated by a whitespace.
    :param data_dir: Directory that contains the interpolation data for the lookup tables.
        By default, the directory of the csv file is used.
    :param extraction_type: str (default: "lookup_tables")
        Data to be extracted from lookup tables. Options are "lookup_tables" or
        "lookup_tables_bounds"

    :return: dict of lookup tables.

    """
    extraction_dict = {}
    lookup_tables_csv = Path(file)
    if not lookup_tables_csv.is_file():
        raise FileNotFoundError(f"File {lookup_tables_csv} not found.")
    if data_dir is None:
        data_dir = lookup_tables_csv.parent
    else:
        data_dir = Path(data_dir)
        if not data_dir.is_dir():
            raise FileNotFoundError(f"Directory {data_dir} not found.")
    lookup_tables_df = pd.read_csv(lookup_tables_csv, sep=",")
    for _, lookup_table_df in lookup_tables_df.iterrows():
        name = lookup_table_df["name"]
        data_csv = Path(data_dir / lookup_table_df["data"])
        var_in: str = lookup_table_df["var_in"]
        var_in = var_in.split(" ")
        var_in = [var for var in var_in if var != ""]
        if extraction_type == "lookup_tables":
            extraction_dict[name] = get_lookup_table_from_csv(
                name=name,
                file=data_csv,
                var_in=var_in,
                var_out=lookup_table_df["var_out"],
            )
        elif extraction_type == "lookup_tables_bounds":
            extraction_dict[name] = get_lookup_table_bounds_from_csv(
                file=data_csv,
                var_in=var_in,
                var_out=lookup_table_df["var_out"],
            )
        else:
            raise ValueError(
                f"extraction_type {extraction_type} not supported "
                'choose from ["lookup_tables", "lookup_tables_bounds"].'
            )

    return extraction_dict


def get_empty_lookup_table(name: str, var_in: Union[str, list[str]], var_out: str) -> ca.Function:
    """
    Get a lookup table that always returns zero.

    :param name: name of the lookup table.
    :param var_in: Input variable(s) of the lookup table.
    :param var_out: Output variable of the lookup table.

    :return: lookup table in the form of a Casadi function.
    """
    vars_in: list[str] = var_in if isinstance(var_in, list) else [var_in]
    del var_out
    var_in_symbols: list[ca.MX] = [ca.MX.sym(var) for var in vars_in]
    lookup_table = ca.Function(name, var_in_symbols, [0])
    return lookup_table


def get_lookup_table_equations_from_csv(
    file: Path,
    lookup_tables: Dict[str, ca.Function],
    variables: Dict[str, ca.MX],
    allow_missing_lookup_tables=False,
) -> List[ca.MX]:
    """
    Get a list of lookup-table equations described by a csv file.

    :param file:
        CSV File that describes equations involving lookup tables.
        These equations are of the form var_out = lookup_table(var_in).
        The csv file consists of the following columns:

        * lookup_table: Name of the lookup table.

        * var_in: Input variable(s) of the lookup table. Should be defined in the model.
          In case of multiple input variables, they should be separated by a whitespace.

        * var_out: Output variable of the lookup table. Should be defined in the model.

    :param lookup_tables: Dict of lookup tables.
    :param variables: Dict of symbolic variables used in the model.
    :param allow_missing_lookup_tables: If True, replace missing lookup tables with empty tables.

    :return: list of equations.
    """
    equations = []
    equations_csv = Path(file)
    assert equations_csv.is_file()
    equations_df = pd.read_csv(equations_csv, sep=",")
    for _, equation_df in equations_df.iterrows():
        name = equation_df["lookup_table"]
        var_in: str = equation_df["var_in"]
        var_in = var_in.split(" ")
        var_in = [var for var in var_in if var != ""]
        var_out = equation_df["var_out"]
        if name not in lookup_tables:
            if allow_missing_lookup_tables:
                lookup_table = get_empty_lookup_table(name, var_in, var_out)
            else:
                raise ValueError(f"Lookup table {name} not found.")
        else:
            lookup_table = lookup_tables[name]
        var_in_mx = [variables[var] for var in var_in]
        var_out_mx = variables[var_out]
        if not lookup_table.n_in() == len(var_in):
            error = (
                f"Lookup table {name} has wrong number of inputs: {lookup_table.n_in()}."
                f" Expected {len(var_in)} inputs: {var_in}."
            )
            raise AssertionError(error)
        equations.append(lookup_table(*var_in_mx) - var_out_mx)
    return equations
