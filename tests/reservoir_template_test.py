"""Test building a reservoir model template."""
import pathlib
import subprocess
import sys

import pytest
from rtctools_simulation.reservoir.template import create_reservoir_dir

RESERVOIR_DIR = pathlib.Path(__file__).parent.resolve() / "reservoir_template"


@pytest.mark.parametrize(
    "allow_overwrite,expected_success",
    [
        (True, True),
        (False, False),
    ],
)
def test_build_reservoir_template(allow_overwrite, expected_success):
    """Test building and running a reservoir model template."""
    try:
        create_reservoir_dir(
            RESERVOIR_DIR, reservoir_name="TestReservoir", allow_overwrite=allow_overwrite
        )
        success = True
    except ValueError:
        success = False
    assert success == expected_success
    if not success:
        return
    file = RESERVOIR_DIR / "reservoir.py"
    test_run = subprocess.run(
        [sys.executable, file],
        capture_output=True,
        text=True,
        check=False,
    )
    assert test_run.returncode == 0
