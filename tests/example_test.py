"""Test that all examples run."""
import pathlib
import subprocess
import sys

import pytest

EXAMPLE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "examples"


@pytest.mark.parametrize(
    "example",
    [str(path.relative_to(EXAMPLE_DIR)) for path in EXAMPLE_DIR.rglob("*.py")],
)
def test_example(example: pathlib.Path):
    """Test if a given example runs successfully."""
    example = EXAMPLE_DIR / example
    example_run = subprocess.run(
        [sys.executable, example],
        capture_output=True,
        text=True,
        check=False,
    )
    assert example_run.returncode == 0
