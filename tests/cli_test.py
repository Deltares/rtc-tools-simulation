"""Tests for the command line interface."""
import shutil
import subprocess
from pathlib import Path


def test_reservoir_template():
    """Test building a reservoir model template from the command line."""
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
