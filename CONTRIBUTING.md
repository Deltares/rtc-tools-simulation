# Developer Guidelines

## Editable Installation

Make sure to have at least pip 21.3 installed.
Go to the root directory of this project (directory that contains pyproject.toml).
Run `pip install -e . --config-settings editable_mode=compat`.

## Pre-commit Checks

To check the code quality and formatting,
we suggest to use pre-commit.
Install pre-commit by running `pip install pre-commit`.
To setup pre-commit, run `pre-commit install` (only needs to be done once).
Code quality and formatting will then be automatically checked during a commit.

To run the pre-commit check outside of a commit,
run `pre-commit run --all-files --show-diff-on-failure`
from the root directory.

## Test Suite

Make sure that the test suite succeeds before merging a branch into main.
To run the test suite locally,
make sure pytest is installed (`pip install pytest`)
and run `pytest tests` from the project root directory.
