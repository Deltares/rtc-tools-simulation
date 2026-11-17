# Developer Guidelines

## Setting up a Development Environment

You will need Python 3.11 or higher, Git, and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Clone the full repository (the version is taken from git tags) and install it from source:

```bash
git clone https://github.com/Deltares/rtc-tools-simulation.git
cd rtc-tools-simulation
uv sync
```

This installs the package along with the development dependencies, using the versions pinned in `uv.lock`.
Refresh the pinned versions with `uv lock --upgrade`.

Alternatively, with pip 25.1 or newer, in a virtual environment:

```bash
pip install -e . --group dev
```

Plain pip ignores `uv.lock` and resolves the newest versions that `pyproject.toml` allows.

## Pre-commit Checks

To check code quality and formatting, we suggest using pre-commit.
Run this once to set up the hook:

```bash
uvx pre-commit install
```

To run the checks manually:

```bash
uvx pre-commit run --all-files --show-diff-on-failure
```

## Test Suite

Make sure that the test suite succeeds before merging a branch into main:

```bash
uv run pytest tests
```
