"""Example that illustrates use of the adjust scheme
and extracting bounds from lookup tables."""

import logging
import os
import sys
from pathlib import Path

from rtctools.util import run_simulation_problem

import rtctools_simulation.lookup_table as lut
from rtctools_simulation.reservoir.model import InputVar, ModelConfig, ReservoirModel

CONFIG = ModelConfig(base_dir=Path(__file__).parent)
logger = logging.getLogger("rtctools")


class SingleReservoir(ReservoirModel):
    """Example single reservoir model."""

    def pre(self, *args, **kwargs):
        super().pre(*args, **kwargs)

        # We can extract the min and max values in the provided lookup tables within the
        # pre-processing.
        base_folder = Path(sys.path[0])
        lookup_tables_csv = Path(
            os.path.join(os.path.join(base_folder, "lookup_tables"), "lookup_tables.csv")
        )
        lookup_tables_dir = os.path.join(base_folder, "lookup_tables")
        lookup_tables_bounds = lut.get_lookup_tables_bounds_from_csv(
            file=lookup_tables_csv, data_dir=lookup_tables_dir
        )
        logger.info(
            "Volumes in the lookup table 'h_from_v' are in the range "
            f"{lookup_tables_bounds['h_from_v']['volume_m3']}"
        )
        logger.info(
            "Elevations in the lookup table 'v_from_h' are in the range "
            f"{lookup_tables_bounds['v_from_h']['height_m']}"
        )

    def apply_schemes(self):
        """Apply schemes for controlling the reservoir."""

        # Apply schemes.
        self.set_q(
            target_variable=InputVar.Q_OUT,
            input_type="parameter",
            input_data=0.4,
        )
        self.apply_adjust()


# Create and run the model.
if __name__ == "__main__":
    run_simulation_problem(SingleReservoir, config=CONFIG)
