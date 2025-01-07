"""Module for simulating a model."""
import logging

import rtctools.util


def simulate(model_class, model_kwargs: dict, log_level=logging.INFO):
    """Run a simualation problem, given the model class."""
    model = rtctools.util.run_simulation_problem(model_class, log_level=log_level, **model_kwargs)
    return model
