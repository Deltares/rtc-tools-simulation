from rtctools.simulation.csv_mixin import CSVMixin
from rtctools.simulation.simulation_problem import SimulationProblem
from rtctools.util import run_simulation_problem
from rtctools_interface.simulation.plot_mixin import PlotMixin


class SingleReservoir(PlotMixin, CSVMixin, SimulationProblem):
    def initialize(self):
        self.set_var("Q_out", 0)
        super().initialize()

    def update(self, dt):
        self.set_var("Q_out", 1)
        super().update(dt)


run_simulation_problem(SingleReservoir)
