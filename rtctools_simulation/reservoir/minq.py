"""Module for the qmin scheme.

The qmin scheme determines the outflow based on an optimization problem.
"""
from datetime import datetime
from typing import List, Optional

import numpy as np
import pydantic
from rtctools.optimization.goal_programming_mixin import Goal, GoalProgrammingMixin

from rtctools_simulation.model_config import ModelConfig
from rtctools_simulation.optimization_problem import OptimizationProblem
from rtctools_simulation.reservoir._variables import InputVar, OptimizationVar, OutputVar


class QMinParameters(pydantic.BaseModel):
    """Data class containing qmin-specific parameters."""

    h_min: pydantic.NonNegativeFloat = 0
    h_max: Optional[pydantic.NonNegativeFloat] = None
    h_target: pydantic.NonNegativeFloat
    q_flood: pydantic.NonNegativeFloat = 0


class MinimizeQOutMax(Goal):
    """Goal for minimizing the peak outflow."""

    priority = 1

    def function(self, optimization_problem, ensemble_member):
        return optimization_problem.state(OptimizationVar.Q_OUT_MAX.value)


class TargetElevation(Goal):
    """Goal for a target elevation."""

    priority = 2

    def __init__(self, h_target):
        self.h_target = h_target

    def function(self, optimization_problem, ensemble_member):
        return optimization_problem.state(OutputVar.HEIGHT.value) - self.h_target


class QMinProblem(OptimizationProblem, GoalProgrammingMixin):
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

    def lookup_table_equations(self, allow_missing_lookup_tables=True):
        return super().lookup_table_equations(allow_missing_lookup_tables)

    def pre(self):
        self.io.reference_datetime = self.datetimes[0]
        for var, value in self.input_timeseries.items():
            self.io.set_timeseries(var.value, self.datetimes, np.array(value))
        super().pre()

    def times(self, variable=None):
        return self.io.datetime_to_sec(self.datetimes, self.datetimes[0])

    def path_goals(self):
        return [*super().path_goals(), MinimizeQOutMax(), TargetElevation(self.params.h_target)]

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
            OutputVar.HEIGHT.value: (self.params.h_min, self.params.h_max),
            OutputVar.Q_OUT.value: (0, np.inf),
            OptimizationVar.Q_OUT_MAX.value: (self.params.q_flood, np.inf),
        }
