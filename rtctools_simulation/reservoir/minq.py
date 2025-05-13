"""Module for the qmin scheme.

The qmin scheme determines the outflow based on an optimization problem.
"""
from datetime import datetime
from typing import List, Optional, Union

import numpy as np
import pydantic
from rtctools.optimization.goal_programming_mixin import Goal

from rtctools_simulation.model_config import ModelConfig
from rtctools_simulation.optimization_problem import OptimizationProblem
from rtctools_simulation.reservoir._variables import InputVar, OptimizationVar, OutputVar


class QMinParameters(pydantic.BaseModel):
    """Data class containing qmin-specific parameters in terms of volume."""

    v_min: pydantic.NonNegativeFloat = 0
    v_max: Optional[pydantic.NonNegativeFloat] = None
    v_target: Union[pydantic.NonNegativeFloat, List[pydantic.NonNegativeFloat]]
    q_flood: pydantic.NonNegativeFloat = 0


class VolumeBounds(Goal):
    """Goal to set limits on elevation."""

    priority = 1

    def __init__(self, v_min, v_max):
        self.target_min = v_min
        self.target_max = v_max
        # Set the function range via the range provided for min and max volume.
        self.function_range = [v_min - abs(v_min) - 1, 2 * v_max]

    def function(self, optimization_problem, ensemble_member):
        return optimization_problem.state(OutputVar.VOLUME.value)


class MinimizeQOutMax(Goal):
    """Goal for minimizing the peak outflow."""

    priority = 2

    def function(self, optimization_problem, ensemble_member):
        return optimization_problem.state(OptimizationVar.Q_OUT_MAX.value)


class TargetVolume(Goal):
    """Goal for a target volume."""

    priority = 3

    def __init__(self, v_target: Union[float, List[float]], v_min, v_max):
        self.target_max = v_target
        self.target_min = v_target
        self.function_range = [v_min - abs(v_min) - 1, 2 * v_max]

    def function(self, optimization_problem: OptimizationProblem, ensemble_member):
        return optimization_problem.state(OutputVar.VOLUME.value)


class QMinProblem(OptimizationProblem):
    """Class for describing an outflow optimization problem."""

    def __init__(
        self,
        config: ModelConfig,
        datetimes: List[datetime],
        params: QMinParameters,
        input_timeseries: dict[InputVar],
        **kwargs,
    ):
        self.datetimes = datetimes
        self.params = params
        self.input_timeseries = input_timeseries
        super().__init__(config, **kwargs)

    def pre(self):
        self.io.reference_datetime = self.datetimes[0]
        for var, value in self.input_timeseries.items():
            self.io.set_timeseries(var.value, self.datetimes, np.array(value))
        super().pre()

    def times(self, variable=None):
        return self.io.datetime_to_sec(self.datetimes, self.datetimes[0])

    def goals(self):
        return [
            *super().goals(),
        ]

    def path_goals(self):
        return [
            *super().path_goals(),
            VolumeBounds(self.params.v_min, self.params.v_max),
            MinimizeQOutMax(),
            TargetVolume(
                v_target=self.params.v_target, v_max=self.params.v_max, v_min=self.params.v_min
            ),
        ]

    def path_constraints(self, ensemble_member):
        q_out = self.state(OutputVar.Q_OUT.value)
        q_out_max = self.state(OptimizationVar.Q_OUT_MAX.value)
        return [
            *super().path_constraints(ensemble_member),
            (q_out_max - q_out, 0, np.inf),
        ]

    def bounds(self):
        return {
            **super().bounds(),
            OutputVar.Q_OUT.value: (0, np.inf),
            OptimizationVar.Q_OUT_MAX.value: (self.params.q_flood, np.inf),
        }
