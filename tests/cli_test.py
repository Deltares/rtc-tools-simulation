"""Tests for the command line interface."""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_reservoir_template():
    """Test building a reservoir model template from the command line."""
    script = shutil.which("rtc-tools-reservoir-template")
    if script is None:
        # Hacky way to ensure that rtc-tools-reservoir-template can be found.
        # This normally seems to be the case except for some specific debug modes.
        os.environ["PATH"] += os.pathsep + str(Path(sys.executable).parent)
        script = shutil.which("rtc-tools-reservoir-template")
    assert script is not None, "Unable to find the rtc-tools-reservoir-template executable."
    test_run = subprocess.run(
        [
            script,
            "-f",
            "-d",
            "reservoir_template_from_cli",
            "-n",
            "TestReservoir",
        ],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
        check=False,
    )
    assert test_run.returncode == 0
