.. _initial-conditions:

Initial Conditions
==================

The user can set intial conitions via the variables for ``H_observed``, ``H``, or ``V``.

* If the user provides a value at t0 for ``H_observed``, this will be used as the initial elevation.
* Else if the user provides a value at t0 for ``H``, this will be used as the initial elevation.
* Else if the user provides a value at t0 for ``V``, this will be used as the initial elevation.

Both lookup tables ``h_from_v`` and ``v_from_h`` are required by the model for setting initial conditions.