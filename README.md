# rtc-tools-simulation

This is rtc-tools-simulation, a toolbox for simulation model building for [rtc-tools](https://gitlab.com/deltares/rtc-tools).

## Install

```bash
pip install rtc-tools-simulation
```

## Documentation

Documentation and examples can be found on [readthedocs](https://rtc-tools-simulation.readthedocs.io).

To build the documentation, the required dependencies are in the `docs` dependency group from `pyproject.toml`.
Run these commands from the repository root:

```bash
uv sync --group docs
uv run sphinx-build -b html docs/source docs/build/html
```

With pip (version 25.1 or newer), use `pip install -e . --group docs` and `sphinx-build -b html docs/source docs/build/html` instead.

The built HTML pages will be in `docs/build/html/`.

## Development

Python 3.11 or newer is required. Install the project with its development dependencies and run the tests from the repository root, with either [uv](https://docs.astral.sh/uv/) or plain pip.

With uv:

```bash
uv sync
uv run pytest tests
```

`uv.lock` pins the dependency versions; refresh it with `uv lock --upgrade`.

With pip (version 25.1 or newer, for `--group`), in a virtual environment:

```bash
pip install -e . --group dev
pytest tests
```

Plain pip resolves the newest dependency versions that `pyproject.toml` allows and ignores `uv.lock`.

## Developer guidelines

Developer guidelines can be found [here](https://gitlab.com/rtc-tools-project/rtc-tools-simulation/-/blob/main/CONTRIBUTING.md)
