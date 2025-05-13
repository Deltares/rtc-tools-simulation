"""Module for an optimization problem class to be solved during simulation."""
import logging
from typing import Dict

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
