"""List of all reservoir model variables."""
from enum import Enum
from typing import Literal


class InputVar(str, Enum):
    """Reservoir model input variable."""

    # Outflow controls
    Q_OUT = "Q_out_from_input"  #: outflow (m^3/s)
    Q_TURBINE = "Q_turbine"  #: turbine outflow (m^3/s)
    Q_SLUICE = "Q_sluice"  #: sluice outflow (m^3/s)
    # Fixed inputs
    H_OBSERVED = "H_observed"  #: observed water height (m)
    Q_IN = "Q_in"  #: inflow (m^3/s)
    Q_EVAP = "mm_evaporation_per_hour"  #: evaporation (mm/hour)
    Q_RAIN = "mm_rain_per_hour"  #: rain (mm/hour)
    # Scheme inputs
    DO_SPILL = "do_spill"
    DO_PASS = "do_pass"
    DO_POOL_Q = "do_poolq"
    DO_SET_Q_OUT = "do_set_q_out"
    USE_COMPOSITE_Q = "use_composite_q"
    INCLUDE_EVAPORATION = "include_evaporation"
    INCLUDE_RAIN = "include_rain"
    # Time inputs
    DAY = "day"


class OutputVar(str, Enum):
    """Reservoir model output variable."""

    VOLUME = "V"  #: water volume (m^3)
    HEIGHT = "H"  #: water height (m)
    Q_OUT = "Q_out"  #: outflow (m^3/s)
    Q_EVAP = "Q_evap"  #: evaporation (m^3/s)
    Q_RAIN = "Q_rain"  #: rain (m^3/s)
    Q_SPILL = "Q_spill"  #: spill (m^3/s)


class OptimizationVar(str, Enum):
    """Variables for reservoir model optimization."""

    Q_OUT_MAX = "Q_out_max"  #: maximum outflow (m^3/s)


#: Reservoir outflow control variables.
QOutControlVar = Literal[
    InputVar.Q_OUT,
    InputVar.Q_TURBINE,
    InputVar.Q_SLUICE,
]


#: Fixed input variables.
FixedInputVar = Literal[
    InputVar.H_OBSERVED,
    InputVar.Q_IN,
    InputVar.Q_EVAP,
    InputVar.Q_RAIN,
]


#: Scheme variables.
SchemeVar = Literal[
    InputVar.DO_SPILL,
    InputVar.DO_PASS,
    InputVar.DO_POOL_Q,
    InputVar.DO_SET_Q_OUT,
    InputVar.USE_COMPOSITE_Q,
    InputVar.INCLUDE_EVAPORATION,
    InputVar.INCLUDE_RAIN,
]


#: State variables.
StateVar = Literal[OutputVar.VOLUME,]
