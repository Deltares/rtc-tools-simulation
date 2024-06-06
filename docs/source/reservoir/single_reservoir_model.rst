.. _single-reservoir-model:

Single Reservoir Model
======================

When modelling a single reservoir, the user does not need to create his own model file.
Instead, the :py:class:`ReservoirModel` class will use a default model file.
Details of this model file will be described here.
Note that it is not necessary to understand these details
in order to use :py:class:`ReservoirModel`,
but it provides some insight into how things work under the hood.
The model is written in the modeilca language.
Here we describe the model assumptions, and include the model itself for the interested user.

The single reservoir is modelled as having a single inflow, and single outflow. This outflow can be made up of components
flowing through a spillway or turbine if applicable (activated through the use of schemes, see :ref:`reservoir-api`). 
The reservoir has an associated elevation, and volume.
It is also possible to account for the effects of rain or evaporation (see :ref:`reservoir-api`).

Inputs
------

``input`` variables are required for the simulation model to run. 

* ``V_observed``: The observed volume of the reservoir
* ``Q_in``: The inflow into the reservoir.
* ``Q_turbine``: The outflow from the reservoir which flows through a turbine.
* ``Q_sluice``: The outflow from the reservoir which flows through a sluice.
* ``do_spill``: A boolean which determines whether or not the spillway scheme is applied.
* ``do_pass``: A boolean which determines whether or not the passflow scheme is applied.
* ``do_poolq``: A boolean which determines whether or not the poolq scheme is applied.
* ``compute_v``: A boolean which determines whether or not the adjust scheme is applied.
* ``include_evaporation``: A boolean which determines whether or not evaporation is accounted for.
* ``include_rain``: A boolean which determines whether or not rain is accounted for.
* ``mm_evaporation_per_hour``: The evaporation from the reservoir (mm per hour).
* ``mm_rain_per_hour``: The rain falling in the reservoir (mm per hour).
* ``Q_out_from_input``: The total outflow of the reservoir if set by the user using the ``set_q`` scheme. 
* ``do_set_q_out``: A boolean which determines whether or total reservoir outflow is set by applying the ``set_q`` scheme.

For variables such as ``Q_in``, ``Q_turbine``, ``Q_sluice``, ``mm_evaporation_per_hour``, ``Q_out_from_input`` and ``mm_rain_per_hour``,
default values are set via 
the python script if they are not provided by the user. These defaults do not negatively affect the solution, but allow the 
script to run if the user is not interested in considering a turbine flow for instance, or wishes to set reservoir inflow via a scheme. 

``compute_v`` has a default of True, as the volume of the reservoir is always computed by the simulation, unless the
adjust scheme is applied. All other input booleans which refer to the application of schemes have a default of ``False``. 

Outputs
-------

``output`` variables are calculated during the simulation run. 

* ``V``: The volume of the reservoir.
* ``Q_out``: The outflow from the reservoir.
* ``Q_out_corrected``: The corrected outflow of the reservoir given observed volumes if the adjust schme is applied.
* ``Q_error``: The difference in precalculated Q_out and the observed Volume change, used by the adjust scheme.
* ``H``: The elevation of the reservoir.
* ``Q_evap``: The amount of water leaving the reservoir at each timestep due to evaporation.
* ``Q_rain``: The amount of water entering the reservoir at each timestep due to rain.
* ``Q_spill``: The outflow from the reservoir which flows through a spillway.

There are various states which are used to aid calculations, but are not outputs from the model. These include;

* ``Q_out_from_lookup_table``: The outflow from the reservoir read from a lookup table.
* ``Area``: The area of the reservoir.
* ``Q_spill_from_lookup_table``: The outflow through the spillway as given by a lookup table.

Parameters
----------

Parameters have fixed values for times during the simulation run. The model considers the following parameters;

* ``H_crest``: The crest level of the reservoir.
* ``max_reservoir_area``: The maximum area of the reservoir.

Units
-----

The unit of each paramter/input/output variable can be seen when it is defined. The standard units library of Modelica is used. 
The flow per unit area is not defined in this library, thus we define it as;

``type FlowRatePerArea = Real(unit = "mm/hour");``

The Modelica model
------------------

``reservoir.mo`` file contains the default model for a single reservoir. In text mode, the Modelica model looks as follows

.. literalinclude:: ../../../rtctools_simulation/modelica/reservoir/reservoir.mo
  :language: modelica
  :lineno-match:

.. note::

      Modelica is not a programming language, but just describes the equations and variables that form a model.
      Therefore, equations in Modelica just equate expressions as opposed to assigning the value of one variable
      to another like in Python.