"""Module for a basic model."""
import logging
from pathlib import Path
from typing import Dict, List

import casadi as ca
from rtctools.simulation.pi_mixin import PIMixin
from rtctools.simulation.simulation_problem import SimulationProblem
from rtctools_interface.simulation.plot_mixin import PlotMixin

import rtctools_simulation.lookup_table as lut
from rtctools_simulation.model_config import ModelConfig

logger = logging.getLogger("rtctools")


class _SimulationProblem(SimulationProblem):
    """
    Class to enable setting input after reading files.
    """

    def set_input_variables(self):
        """Set input variables."""
        pass

    def initialize(self, config_file=None):
        self.set_input_variables()
        super().initialize(config_file)

    def update(self, dt):
        # Temporarily update the time to set input variables.
        # TODO: Ideally, rtc-tools allows for preprocessing before calling update.
        # For now, temporarily updating the time provides a workaround.
        if dt > 0:
            self.set_time_step(dt)
        dt = self.get_time_step()
        t_old = self.get_current_time()
        t_new = t_old + dt
        self.set_var("time", t_new)
        self.set_input_variables()
        # Restore the time and call super().update.
        self.set_var("time", t_old)
        super().update(dt)


class Model(PlotMixin, PIMixin, _SimulationProblem):
    """Basic model class."""

    def __init__(self, config: ModelConfig, **kwargs):
        self._config = config
        self._lookup_tables = self._get_lookup_tables()
        self.plot_table_file = self._get_plot_table_file()
        kwargs["input_folder"] = str(self._config.get_dir("input"))
        kwargs["output_folder"] = str(self._config.get_dir("output"))
        kwargs["model_folder"] = str(self._config.get_dir("model"))
        kwargs["model_name"] = str(self._config.model())
        super().__init__(**kwargs)

    def _get_plot_table_file(self):
        """Get the file that describes the plots."""
        plot_table_file = self._config.get_file("plot_table.csv", dirs=["input"])
        if plot_table_file is None:
            plot_table_file = Path(__file__).parent / "empty_plot_table.csv"
        return plot_table_file

    def _get_lookup_tables(self) -> Dict[str, ca.Function]:
        """Get a dict of lookup tables."""
        lookup_tables_csv = self._config.get_file("lookup_tables.csv", dirs=["lookup_tables"])
        if lookup_tables_csv is None:
            logger.debug("No lookup tables found.")
            return {}
        lookup_tables_dir = self._config.get_dir("lookup_tables")
        if lookup_tables_dir is None:
            raise FileNotFoundError("Directory lookup_tables not found.")
        lookup_tables = lut.get_lookup_tables_from_csv(
            file=lookup_tables_csv, data_dir=lookup_tables_dir
        )
        return lookup_tables

    def lookup_tables(self) -> Dict[str, ca.Function]:
        """Return a dict of lookup tables."""
        return self._lookup_tables

    def lookup_table(self, lookup_table: str) -> ca.Function:
        """Return a lookup table."""
        return self._lookup_tables[lookup_table]

    def _get_lookup_table_equations(self, allow_missing_lookup_tables=False) -> List[ca.MX]:
        """Get a list of lookup-table equations."""
        equations_csv = self._config.get_file("lookup_table_equations.csv", dirs=["model"])
        if equations_csv is None:
            logger.debug("No lookup table equations found.")
            return []
        lookup_tables = self.lookup_tables()
        variables = self.get_variables()
        equations = lut.get_lookup_table_equations_from_csv(
            file=equations_csv,
            lookup_tables=lookup_tables,
            variables=variables,
            allow_missing_lookup_tables=allow_missing_lookup_tables,
        )
        return equations

    def extra_equations(self) -> List[ca.MX]:
        equations = super().extra_equations()
        lookup_table_equations = self._get_lookup_table_equations()
        equations.extend(lookup_table_equations)
        return equations

    def post(self):
        """Tasks after simulating."""
        self.calculate_output_variables()
        super().post()

    def calculate_output_variables(self):
        """
        Calculate output variables.

        This method is called after the simulation has finished.
        The user can implement this method to calculate additional output variables.
        """
        pass
