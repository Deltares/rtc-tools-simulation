import logging
from pathlib import Path

import numpy as np
import pytest

from rtctools_simulation_modelling_extension.reservoir.model import ModelConfig, ReservoirModel
from rtctools_simulation_modelling_extension.reservoir.setq_help_functions import (
    NoDataException,
)

logger = logging.getLogger("rtctools")

ts = [1, 2, 3, 1, 3, 5]
nan_ts_1 = [1, 2, 3, 7, np.nan, 5]
nan_ts_0 = [np.nan, 2, 3, 7, 3, 5]
nan_ts_5 = [5, 2, 3, 7, 3, np.nan]
nan_ts_interp = [5, 7, np.nan, np.nan, np.nan, 3]
all_nan = [np.nan] * 6
nan_end = [5, 7, np.nan, np.nan, np.nan, np.nan]


@pytest.mark.parametrize(
    "apply_func, input_data, input_type, timestep, nan_option, expected",
    [
        ## Test whole timeseries statistics
        ("MEAN", ts, "timeseries", None, None, 2.5),
        ("MEAN", nan_ts_1, "timeseries", None, None, 3.6),
        ("MIN", ts, "timeseries", None, None, 1),
        ("MIN", nan_ts_1, "timeseries", None, None, 1),
        ("MAX", ts, "timeseries", None, None, 5),
        ("MAX", nan_ts_1, "timeseries", None, None, 7),
        ## Test data selection through 't'
        ("INST", ts, "timeseries", 2, None, 3),
        ("INST", nan_ts_1, "timeseries", 4, "NEXT", 5),
        ("INST", nan_ts_5, "timeseries", 5, "NEXT", NoDataException),  ## No data beyond index 5
        ("INST", nan_ts_1, "timeseries", 4, "MEAN", 3.6),
        ("INST", nan_ts_1, "timeseries", 4, "PREV", 7),
        ("INST", nan_ts_1, "timeseries", 4, "CLOSEST", 6),
        ("INST", nan_ts_1, "timeseries", 4, "INTERP", 6),
        ("INST", nan_ts_interp, "timeseries", 4, "INTERP", 4),
        ("INST", nan_ts_interp, "timeseries", 3, "INTERP", 5),
        ("INST", nan_ts_0, "timeseries", 0, "PREV", NoDataException),  # No previous data
        ("INST", all_nan, "timeseries", 3, "PREV", NoDataException),  # No previous data
        ("INST", all_nan, "timeseries", 3, "NEXT", NoDataException),  # No future data
        ("INST", all_nan, "timeseries", 3, "CLOSEST", NoDataException),  # No data at all
        ("INST", all_nan, "timeseries", 3, "INTERP", NoDataException),  # No data at all
        (
            "INST",
            nan_end,
            "timeseries",
            3,
            "INTERP",
            7,
        ),  # Default to closest when only 1 side has data
        ("INST", nan_end, "timeseries", 3, "CLOSEST", 7),
        ("INST", 4, "parameter", None, None, 4),  ## Test Parameter option
        ## Test setq from internal variable 1 step ahead
        ("INST", "Q_in", "timeseries", 3, None, 3.8080494),
        ("INST", "Q_in", "timeseries", None, None, 3.7766178),  ## Test setq from internal variable
    ],
)
def test_set_q(apply_func, input_data, input_type, timestep, nan_option, expected):
    setq_dir = Path(__file__).parent.resolve() / "set_q"

    class SingleReservoir(ReservoirModel):
        def apply_schemes(self):
            test_time_s = 7200
            if self.get_current_time() == test_time_s:
                try:
                    self.set_q(
                        target_variable="Q_turbine",
                        input_type=input_type,
                        input_data=input_data,
                        apply_func=apply_func,
                        nan_option=nan_option,
                        timestep=timestep,
                    )
                    q_result = self.get_var("Q_turbine")
                except NoDataException:
                    q_result = NoDataException
                assert expected == q_result

    config = ModelConfig(base_dir=setq_dir)
    model = SingleReservoir(config)
    model.simulate()
