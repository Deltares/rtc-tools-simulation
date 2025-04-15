"""Module for organising the reservoir model input.

All the input of the reservoir model can be organised in one object.
This makes it easier to set, validate, and analyse the input variables.
"""

from enum import Enum
from typing import Annotated, Optional

import pydantic

from rtctools_simulation.reservoir._variables import InputVar


class Volume(pydantic.BaseModel):
    h_observed: pydantic.NonNegativeFloat = 0


class RainEvap(pydantic.BaseModel):
    """Rain/evaporation input."""

    include_evaporation: bool = False
    include_rain: bool = False
    mm_evaporation_per_hour: pydantic.NonNegativeFloat = 0
    mm_rain_per_hour: pydantic.NonNegativeFloat = 0


class OutflowType(str, Enum):
    PASS = "pass"
    LOOKUP_TABLE = "lookup_table"
    COMPOSITE = "composite"
    FROM_INPUT = "from_input"


class OutflowComponent(str, Enum):
    TURBINE = "turbine"
    SLUICE = "sluice"


class OutflowComponents(pydantic.BaseModel):
    do_spill: bool = False
    turbine: pydantic.NonNegativeFloat = 0
    sluice: pydantic.NonNegativeFloat = 0


class Outflow(pydantic.BaseModel):
    outflow_type: OutflowType = OutflowType.COMPOSITE
    components: Optional[OutflowComponents] = None
    from_input: pydantic.NonNegativeFloat = 0
    optimized: pydantic.NonNegativeFloat = 0

    @pydantic.model_validator(mode="after")
    def set_defaults(self) -> "Outflow":
        if self.components is None or self.outflow_type != OutflowType.COMPOSITE:
            self.components = OutflowComponents()
        return self


class Input(pydantic.BaseModel):
    volume: Optional[Volume] = None
    inflow: float = 0
    rain_evap: Optional[RainEvap] = None
    outflow: Optional[Outflow] = None
    day: Annotated[int, pydantic.Field(ge=1, le=31)] = 1

    @pydantic.model_validator(mode="after")
    def set_defaults(self) -> "Input":
        if self.volume is None:
            self.volume = Volume()
        if self.rain_evap is None:
            self.rain_evap = RainEvap()
        if self.outflow is None:
            self.outflow = Outflow()
        return self


def input_to_dict(model_input: Input) -> dict[InputVar]:
    """Convert an Input object to a dict."""
    return {
        InputVar.Q_OUT: model_input.outflow.from_input,
        InputVar.Q_TURBINE: model_input.outflow.components.turbine,
        InputVar.Q_SLUICE: model_input.outflow.components.sluice,
        InputVar.H_OBSERVED: model_input.volume.h_observed,
        InputVar.Q_IN: model_input.inflow,
        InputVar.Q_EVAP: model_input.rain_evap.mm_evaporation_per_hour,
        InputVar.Q_RAIN: model_input.rain_evap.mm_rain_per_hour,
        InputVar.DO_SPILL: model_input.outflow.components.do_spill,
        InputVar.DO_PASS: model_input.outflow.outflow_type == OutflowType.PASS,
        InputVar.DO_POOL_Q: model_input.outflow.outflow_type == OutflowType.LOOKUP_TABLE,
        InputVar.DO_SET_Q_OUT: model_input.outflow.outflow_type == OutflowType.FROM_INPUT,
        InputVar.USE_COMPOSITE_Q: model_input.outflow.outflow_type == OutflowType.COMPOSITE,
        InputVar.INCLUDE_EVAPORATION: model_input.rain_evap.include_evaporation,
        InputVar.INCLUDE_RAIN: model_input.rain_evap.include_rain,
        InputVar.DAY: model_input.day,
    }


if __name__ == "__main__":
    pass
