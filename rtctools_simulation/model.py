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

    def initialize_input_variables(self):
        """Initialize input variables."""
        pass

    def set_input_variables(self):
        """Set input variables."""
        pass

    def initialize(self, config_file=None):
        self.initialize_input_variables()
        super().initialize(config_file)

    def update(self, dt):
        """
        Do a basic timestep update.

        This is copied from SimulationProblem.update.
        Only the set

        TODO: a nicer solution should be found rather than
        copying most of an existing method.
        """
        if dt > 0:
            self.set_time_step(dt)
        dt = self.get_time_step()

        logger.debug("Taking a step at {} with size {}".format(self.get_current_time(), dt))

        # increment time
        self.set_var("time", self.get_current_time() + dt)

        # set input variables
        self.set_input_variables()

        # take a step
        guess = self.__state_vector[: self.__n_states]
        if len(self.__mx["parameters"]) > 0:
            next_state = self.__do_step(
                guess, dt, self.__state_vector[: -len(self.__mx["parameters"])]
            )
        else:
            next_state = self.__do_step(guess, dt, self.__state_vector)
        # Check convergence of rootfinder
        rootfinder_stats = self.__do_step.stats()

        if not rootfinder_stats["success"]:
            message = (
                "Simulation has failed to converge at time {}. Solver failed with status {}"
            ).format(self.get_current_time(), rootfinder_stats["nlpsol"]["return_status"])
            logger.error(message)
            raise Exception(message)

        if logger.getEffectiveLevel() == logging.DEBUG:
            # compute max residual
            largest_res = ca.norm_inf(
                self.__res_vals(
                    next_state, self.__dt, self.__state_vector[: -len(self.__mx["parameters"])]
                )
            )
            logger.debug("Residual maximum magnitude: {:.2E}".format(float(largest_res)))

        # Update state vector
        self.__state_vector[: self.__n_states] = next_state.toarray().ravel()


class Model(PlotMixin, PIMixin, _SimulationProblem):
    """Basic model class."""

    def __init__(self, config: ModelConfig, **kwargs):
        self._config = config
        self._lookup_tables = self._get_lookup_tables()
        self.plot_table_file = self._get_plot_table_file()
        super().__init__(
            input_folder=self._config.get_dir("input"),
            output_folder=self._config.get_dir("output"),
            model_folder=self._config.get_dir("model"),
            model_name=self._config.model(),
            **kwargs,
        )

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
        assert lookup_tables_dir is not None, "Directory lookup_tables not found."
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

    def _get_lookup_table_equations(self) -> List[ca.MX]:
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
