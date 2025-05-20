.. _examples-single-reservoir-rainevapexample:

``include_rainevap`` Scheme Example
===================================

This example shows how to use the :py:meth:`.ReservoirModel.include_rainevap` scheme when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``. ``Q_out`` is comprised of two components, 
a spillway, ``Q_sluice``, and a turbine ``Q_turbine``. Flow through the sluice should be 4m3/s and flow through the turbine should 
be 1m3/s. Rainfall and evaporation should be accounted for. 

.. math::
    Q_{out} = Q_{turbine}+Q_{sluice}\\

    Q_{sluice} = 4\\

    Q_{turbine} = 1\\

The :py:meth:`.ReservoirModel.include_rainevap` and :py:meth:`.ReservoirModel.set_q` schemes can be applied to model these operations. 

Main Model (python) File
------------------------

An example of the main model file `rainevap_example.py` is given below.

.. literalinclude:: ../../../../examples/rainevap_example/rainevap_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/rainevap_example/rainevap_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/rainevap_example/rainevap_example.py
  :language: python
  :start-at: class
  :end-at: class

defines a class :py:class:`.SingleReservoir`
that inherits all properties and functionalities
of the predefined class :py:class:`.ReservoirModel`.
An overview of this class can be found in :ref:`reservoir-api`
and details of the underlying model it uses can be found in :ref:`single-reservoir-model`.

The method :py:meth:`.ReservoirModel.apply_schemes` is called every timestep and contains the logic
for which schemes are applied.
The first argument ``self`` is the :py:class:`.SingleReservoir` object itself.
Since :py:class:`.SingleReservoir` inherits from :py:class:`.ReservoirModel`,
``self`` can call any of the :py:class:`.ReservoirModel` methods, such as
:py:meth:`.ReservoirModel.include_rainevap`.
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

The :py:meth:`.ReservoirModel.include_rainevap` scheme is applied to include rain and evaporation in the simulation.
The :py:meth:`.ReservoirModel.set_q` scheme is then applied to set flow through the sluice and the turbine.

.. note::

      To include only rain, ``self.include_rainevap()`` and be replaced with ``self.include_rain()``. Likewise, 
      to include on evaporation, ``self.include_rainevap()`` and be replaced with ``self.include_evaporation()``.


Lookup tables
-------------

This model uses only the standard lookup tables ``h_from_v`` and ``area_from_v``,
for other lookup tables, defaults from the generated template files can be used. 

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

The :py:meth:`.ReservoirModel.include_rainevap` scheme requires and input parameter, ``max_reservoir_area``. This can be provided to the
model via the ``rtcParameterConfig.xml`` input file.

.. literalinclude:: ../../../../examples/rainevap_example/input/rtcParameterConfig.xml
    :language: xml
    :lines: 6-8

The scheme also requires rainfall and evaporation data supplied via the ``timeseries_import.xml``, for evaporation data,

.. literalinclude:: ../../../../examples/rainevap_example/input/timeseries_import.xml
    :language: xml
    :lines: 516-536

and rain data.

.. literalinclude:: ../../../../examples/rainevap_example/input/timeseries_import.xml
    :language: xml
    :lines: 1012-1032

This additional input data is mapped to the internal variables, ``mm_rain_per_hour``, and ``mm_evaporation_per_hour`` using the ``rtcDataConfig.xml``.

.. literalinclude:: ../../../../examples/rainevap_example/input/rtcDataConfig.xml
    :language: xml
    :lines: 19-30

In this example, the :py:meth:`.ReservoirModel.set_q` has been used to set outflows based on an input parameter
``Q_sluice_target``. This parameter is also provided to the model via the ``rtcParameterConfig.xml``.

.. literalinclude:: ../../../../examples/rainevap_example/input/rtcParameterConfig.xml
    :language: xml
    :lines: 9-11

.. note::

      For further details about input file structure please see :ref:`examples-single-reservoir-basic`.

Output Data
-----------

The results of the simulation will appear in the `output` folder
in a file called `timeseries_export.xml`.
The data is linked to model variables via the `rtcDataConfig.xml`
in the same way as with `timeseries_import.xml`.

Automatic Plotting
------------------

You can optionally include a `plot_table.csv` in the input folder.
This is used by the rtc-tools-interfaces module (automatically installed with this package)
to plot the model output.
For more details on how to use this file and visualize results,
see `RTC-Tools-Interface <https://gitlab.com/rtc-tools-project/rtc-tools-interface>`_.

The results of the simulation run can be seen in the plot below. It can be seen that ``Q_evap``
varies with time as it is dependent on the surface area of the reservoir, even though the evaporation per unit area is constant.
``Q_out`` is the sum of ``Q_turbine`` and ``Q_sluice``.

.. raw:: html
    :file: figures/final_results_rainevap.html

