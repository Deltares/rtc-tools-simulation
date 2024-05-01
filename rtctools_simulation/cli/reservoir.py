"""Command line interface for generating a reservoir model template."""
import argparse
import os
from pathlib import Path

from rtctools_simulation.reservoir.template import create_reservoir_dir

parser = argparse.ArgumentParser(description="Build a reservoir model template.")
parser.add_argument(
    "-d",
    "--dir_name",
    type=str,
    help=(
        "Name of the base directory of the reservoir model."
        " The directory will be created in the current working directory."
    ),
    required=True,
)
parser.add_argument(
    "-f", "--force", action="store_true", help="Allow overwriting an existing directory."
)
parser.add_argument("-n", "--name", type=str, help="Name of the reservoir.", required=True)


def create_reservoir_template():
    """Build a reservoir model template file from the command line."""
    args = parser.parse_args()
    reservoir_name = args.name
    dir_name: str = args.dir_name
    dir = Path(os.getcwd()).resolve() / dir_name
    allow_overwrite = args.force
    create_reservoir_dir(dir, reservoir_name=reservoir_name, allow_overwrite=allow_overwrite)
