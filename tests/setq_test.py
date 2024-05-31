import logging
from pathlib import Path

import numpy as np
import pytest

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel
from rtctools_simulation.reservoir.setq_help_functions import (
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
    "target_variable, apply_func, input_data, input_type, timestep, nan_option, expected",
    [
        ## Test whole timeseries statistics
        ("Q_turbine", "MEAN", ts, "timeseries", None, None, 2.5),
        ("Q_turbine", "MEAN", nan_ts_1, "timeseries", None, None, 3.6),
        ("Q_turbine", "MIN", ts, "timeseries", None, None, 1),
        ("Q_turbine", "MIN", nan_ts_1, "timeseries", None, None, 1),
        ("Q_turbine", "MAX", ts, "timeseries", None, None, 5),
        ("Q_turbine", "MAX", nan_ts_1, "timeseries", None, None, 7),
        ## Test data selection through 't'
        ("Q_turbine", "INST", ts, "timeseries", 2, None, 3),
        ("Q_turbine", "INST", nan_ts_1, "timeseries", 4, "NEXT", 5),
        ## No data beyond index 5
        ("Q_turbine", "INST", nan_ts_5, "timeseries", 5, "NEXT", NoDataException),
        ("Q_turbine", "INST", nan_ts_1, "timeseries", 4, "MEAN", 3.6),
        ("Q_turbine", "INST", nan_ts_1, "timeseries", 4, "PREV", 7),
        ("Q_turbine", "INST", nan_ts_1, "timeseries", 4, "CLOSEST", 6),
        ("Q_turbine", "INST", nan_ts_1, "timeseries", 4, "INTERP", 6),
        ("Q_turbine", "INST", nan_ts_interp, "timeseries", 4, "INTERP", 4),
        ("Q_turbine", "INST", nan_ts_interp, "timeseries", 3, "INTERP", 5),
        # No previous data
        ("Q_turbine", "INST", nan_ts_0, "timeseries", 0, "PREV", NoDataException),
        # No previous data
        ("Q_turbine", "INST", all_nan, "timeseries", 3, "PREV", NoDataException),
        # No future data
        ("Q_turbine", "INST", all_nan, "timeseries", 3, "NEXT", NoDataException),
        # No data at all
        ("Q_turbine", "INST", all_nan, "timeseries", 3, "CLOSEST", NoDataException),
        # No data at all
        ("Q_turbine", "INST", all_nan, "timeseries", 3, "INTERP", NoDataException),
        (
            "Q_turbine",
            "INST",
            nan_end,
            "timeseries",
            3,
            "INTERP",
            7,
        ),  # Default to closest when only 1 side has data
        ("Q_turbine", "INST", nan_end, "timeseries", 3, "CLOSEST", 7),
        ("Q_turbine", "INST", 4, "parameter", None, None, 4),  ## Test Parameter option
        ("Q_turbine", None, "target_Q", "parameter", None, None, 4),  ## Test Parameter option
        ## Test setq from internal variable 1 step ahead
        ("Q_turbine", "INST", "Q_in", "timeseries", 3, None, 3.8080494),
        ## Test setq from internal variable
        ("Q_turbine", "INST", "Q_in", "timeseries", None, None, 3.7766178),
        ## Test seting q_out
        ("Q_out", "INST", "Q_in", "timeseries", None, None, 3.7766178),
    ],
)
def test_set_q(target_variable, apply_func, input_data, input_type, timestep, nan_option, expected):
    setq_dir = Path(__file__).parent.resolve() / "set_q"
    test_timestep = 2

    class SingleReservoir(ReservoirModel):
        def apply_schemes(self):
            test_time_s = self.times()[test_timestep]
            if self.get_current_time() == test_time_s:
                self.set_q(
                    target_variable=target_variable,
                    input_type=input_type,
                    input_data=input_data,
                    apply_func=apply_func,
                    nan_option=nan_option,
                    timestep=timestep,
                )

    config = ModelConfig(base_dir=setq_dir)
    model = SingleReservoir(config)
    try:
        model.simulate()
        q_result = model.extract_results()[target_variable][test_timestep]
    except NoDataException:
        q_result = NoDataException
    if expected is NoDataException:
        assert q_result == expected
        return
    np.testing.assert_array_almost_equal(q_result, expected, decimal=3)
