"""Module for a basic model."""
from rtctools.simulation.csv_mixin import CSVMixin
from rtctools.simulation.simulation_problem import SimulationProblem

from rtctools_simulation_modelling_extension.model_config import ModelConfig


class Model(CSVMixin, SimulationProblem):
    """Basic model class."""

    # Configuration
    config: ModelConfig = None

    def __init__(self, **kwargs):
        super().__init__(
            input_folder=self.config.get_dir("input"),
            output_folder=self.config.get_dir("output"),
            model_folder=self.config.get_dir("model"),
            model_name=self.config.model,
            **kwargs,
        )
