# from rtctools_interface.simulation.plot_mixin import PlotMixin
from pathlib import Path

from rtctools_simulation_modelling_extension.reservoir.model import ModelConfig, ReservoirModel


class SingleReservoir(ReservoirModel):
    def initialize(self):
        super().initialize()

    def apply_schemes(self):
        self.set_q(
            target_variable="Q_turbine",
            input_type="parameter",
            input_data=0.01,
        )


# Create and run the model.
if __name__ == "__main__":
    CONFIG = ModelConfig(base_dir=Path(__file__).parent.parent)
    model = SingleReservoir(CONFIG)
    model.simulate()
