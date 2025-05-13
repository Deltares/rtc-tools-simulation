"""Module for testing function to determin flood flag."""
import logging
from pathlib import Path

from rtctools.util import run_simulation_problem

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

BASE_DIR = Path(__file__).parent.resolve() / "basic_model"


class FloodFlagModel(ReservoirModel):
    """Empty model where we get the flood flag in pre."""

    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)
        self.flood_flag = self.get_flood_flag(
            q_out_daily_average=0.0,
            flood_elevation=1.2,
        )


def test_get_flood_flag(log_level=logging.INFO):
    """Test getting the flood flag."""
    config = ModelConfig(base_dir=BASE_DIR)
    model = FloodFlagModel(config)
    model: FloodFlagModel = run_simulation_problem(
        FloodFlagModel, log_level=log_level, config=config
    )
    flood_flag = model.flood_flag
    flood_flag_ref = True
    assert flood_flag == flood_flag_ref
