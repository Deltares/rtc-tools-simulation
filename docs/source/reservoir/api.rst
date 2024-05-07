.. _reservoir-api:

Reservoir API
=============

Methods of the :py:class:`.ReservoirModel` are listed below.
Schemes can be applied by overwriting the :py:meth:`.ReservoirModel.apply_schemes` method.

Available schemes include:

* :py:meth:`.ReservoirModel.apply_spillway`
* :py:meth:`.ReservoirModel.apply_passflow`
* :py:meth:`.ReservoirModel.apply_poolq`
* :py:meth:`.ReservoirModel.apply_rulecurve`
* :py:meth:`.ReservoirModel.apply_adjust`
* :py:meth:`.ReservoirModel.include_rain`
* :py:meth:`.ReservoirModel.include_evaporation`
* :py:meth:`.ReservoirModel.include_rainevap`

An overview of all schemes is given below.

.. autodata:: rtctools_simulation.reservoir.model.VARIABLES

.. autoclass:: rtctools_simulation.reservoir.model.ReservoirModel
  :members:
