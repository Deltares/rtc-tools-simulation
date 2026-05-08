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

The built HTML pages will be in `docs/build/html/`.

## Developer guidelines

Developer guidelines can be found [here](https://gitlab.com/rtc-tools-project/rtc-tools-simulation/-/blob/main/CONTRIBUTING.md)
