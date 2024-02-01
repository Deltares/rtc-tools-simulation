from rtctools.simulation.csv_mixin import CSVMixin
from rtctools.simulation.simulation_problem import SimulationProblem
from rtctools.util import run_simulation_problem


class SingleReservoir(CSVMixin, SimulationProblem):
    def initialize(self):
        self.set_var("Q_out", 0)
        super().initialize()

    def update(self, dt):
        self.set_var("Q_out", 1)
        super().update(dt)


run_simulation_problem(SingleReservoir)
