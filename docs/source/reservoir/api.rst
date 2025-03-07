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
* :py:meth:`.ReservoirModel.set_q`

An overview of all schemes is given below.

.. autoclass:: rtctools_simulation.reservoir._variables.InputVar
  :members:

.. autoclass:: rtctools_simulation.reservoir._variables.OutputVar
  :members:

.. autodata:: rtctools_simulation.reservoir._variables.QOutControlVar

.. autoclass:: rtctools_simulation.reservoir.model.ReservoirModel
  :members:
