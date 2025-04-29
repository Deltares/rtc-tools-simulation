"""Example illustrating the minq scheme."""
from pathlib import Path

from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.minq import QMinParameters
from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)


class Reservoir(ReservoirModel):
    """Class for demonstrating the minq scheme."""

    def apply_schemes(self):
        """Apply minq within a given time period."""
        params = QMinParameters(h_min=0, h_max=40.0, h_target=20, q_flood=0)
        self.apply_minq(params=params)


# Create and run the model.
if __name__ == "__main__":
    model = run_simulation_problem(Reservoir, config=CONFIG, previous_run_plot_config=None)
    results = model.extract_results()
