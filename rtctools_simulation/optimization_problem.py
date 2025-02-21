"""Module for an optimization problem class to be solved during simulation."""
import logging
from typing import Dict, List

import casadi as ca
from rtctools.optimization.collocated_integrated_optimization_problem import (
    CollocatedIntegratedOptimizationProblem,
)
from rtctools.optimization.goal_programming_mixin import GoalProgrammingMixin
from rtctools.optimization.io_mixin import IOMixin
from rtctools.optimization.modelica_mixin import ModelicaMixin

import rtctools_simulation.lookup_table as lut
from rtctools_simulation.model_config import ModelConfig

logger = logging.getLogger("rtctools")


class OptimizationProblem(
    GoalProgrammingMixin, IOMixin, ModelicaMixin, CollocatedIntegratedOptimizationProblem
):
    """
    Basic optimization problem class.

    This class can be used to construct optimization problems
    that need to solved during simulation.
    """

    def __init__(self, config: ModelConfig, **kwargs):
        self._config = config
        # Get lookup tables as casadi functions,
        # not to be confused with rtctools.optimization.optimization_problem.LookupTable objects.
        self._ca_lookup_tables = self._get_lookup_tables()
        kwargs["input_folder"] = str(self._config.get_dir("input"))
        kwargs["output_folder"] = str(self._config.get_dir("output"))
        kwargs["model_folder"] = str(self._config.get_dir("model"))
        kwargs["model_name"] = str(self._config.model())
        super().__init__(**kwargs)

    def _get_lookup_tables(self) -> Dict[str, ca.Function]:
        """Get a dict of lookup tables."""
        lookup_tables_csv = self._config.get_file("lookup_tables.csv", dirs=["lookup_tables"])
        if lookup_tables_csv is None:
            logger.debug("No lookup tables found.")
            return {}
        lookup_tables_dir = self._config.get_dir("lookup_tables")
        if lookup_tables_dir is None:
            raise ValueError("Directory lookup_tables not found.")
        lookup_tables = lut.get_lookup_tables_from_csv(
            file=lookup_tables_csv, data_dir=lookup_tables_dir
        )
        return lookup_tables

    def ca_lookup_tables(self) -> Dict[str, ca.Function]:
        """Return a dict of lookup tables of type casadi functions."""
        return self._ca_lookup_tables

    def ca_lookup_table(self, lookup_table: str) -> ca.Function:
        """Return a lookup table of type casadi function."""
        return self._ca_lookup_tables[lookup_table]

    def read(self):
        pass

    def write(self):
        pass

    def variables(self) -> Dict[str, ca.MX]:
        """Return a list of all the variables."""
        var_types = [
            "time",
            "states",
            "algebraics",
            "parameters",
            "control_inputs",
            "constant_inputs",
        ]
        # TODO: perhaps this should be an rtctools.AliasDict, but this class is private.
        variables = {}
        for var_type in var_types:
            var_syms: list[ca.MX] = self.dae_variables[var_type]
            variables.update({var_sym.name(): var_sym for var_sym in var_syms})
        return variables

    def lookup_table_equations(self, allow_missing_lookup_tables=False) -> List[ca.MX]:
        """Return a list of lookup-table equations."""
        equations_csv = self._config.get_file("lookup_table_equations.csv", dirs=["model"])
        if equations_csv is None:
            logger.debug("No lookup table equations found.")
            return []
        lookup_tables = self._ca_lookup_tables
        variables = self.variables()
        equations = lut.get_lookup_table_equations_from_csv(
            file=equations_csv,
            lookup_tables=lookup_tables,
            variables=variables,
            allow_missing_lookup_tables=allow_missing_lookup_tables,
        )
        return equations

    @property
    def dae_residual(self) -> ca.MX:
        dae_residual = super().dae_residual
        lookup_table_equations = self.lookup_table_equations()
        return ca.veccat(dae_residual, *lookup_table_equations)
