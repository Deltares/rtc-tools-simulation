"""Test that all examples run."""
import pathlib
import subprocess
import sys

import pytest

EXAMPLE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "examples"


@pytest.mark.parametrize(
    "example",
    [
        "single_reservoir/single_reservoir.py",
    ],
)
def test_example(example: pathlib.Path):
    """Test if a given example runs succesfully."""
    example = EXAMPLE_DIR / example
    example_run = subprocess.run(
        [sys.executable, example],
        capture_output=True,
        text=True,
        check=False,
    )
    assert example_run.returncode == 0
