.. _examples-single-reservoir-fillspillexample:

``apply_fillspill`` Scheme Example
==================================

This example shows how to use the :py:meth:`.ReservoirModel.apply_fillspill` scheme when modelling a single reservoir model.
It will aim to satisfy a certain target elevation, fill if below it, and spill if it exceeds a threshold elevation.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``. ``Q_out`` is comprised of two components,
a turbine, ``Q_turbine``, and a spillway, ''Q_spill''.
The scheme requires the presence of several parameters in the file 'input/rtcParameterConfig.xml'.

"Reservoir_Htarget": Elevation that the scheme tries to satisfy at minimum.
"Spillway_H": elevation above which the spillway will be activated according to the Q/H relationship.
"Reservoir_Qmax": Maximum turbine discharge
"Reservoir_Qmin": Minimum turbine discharge demand, for example based on energy demand or downstream water demand

Main Model (python) File
------------------------

An example of the main model file `fillspill_example.py` is given below.

.. literalinclude:: ../../../../examples/fillspill_example/fillspill_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/fillspill_example/fillspill_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/fillspill_example/fillspill_example.py
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
:py:meth:`.ReservoirModel.apply_fillspill`.
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

The :py:meth:`.ReservoirModel.apply_fillspill` scheme is then applied to set the reservoir outflow through the turbine.
It will minimally release water when H < Reservoir_Htarget, pass the inflow when Reservoir_Htarget < H < Spillway_H,
and spill when H exceeds Spillway_H. Furthermore, it considers the limits on the discharge through the turbine.


Lookup tables
-------------

The :py:meth:`.ReservoirModel.apply_fillspill` scheme uses a lookup table ``v_from_h``. This  uses the same
data as the ``h_from_v`` lookup table, the data mapping can be achieved in the ``lookup_tables.csv`` file.

.. csv-table:: <base_dir>/lookup_tables/lookup_tables.csv
  :file: ../../../../examples/fillspill_example/lookup_tables/lookup_tables.csv
  :header-rows: 1

This model also uses the standard lookup table ``h_from_v``.
For other lookup tables, defaults from the generated template files can be used. 

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

The :py:meth:`.ReservoirModel.apply_fillspill` scheme requires the following parameters from the ``rtcParameterConfig.xml`` file.
"Reservoir_Htarget": Elevation that the scheme tries to satisfy at minimum.
"Spillway_H": elevation above which the spillway will be activated according to the Q/H relationship.
"Reservoir_Qmax": Maximum turbine discharge
"Reservoir_Qmin": Minimum turbine discharge demand, for example based on energy demand or downstream water demand

These parameters are supplied to the model via the ``rtcParameterConfig.xml`` input file.

.. literalinclude:: ..\\..\\..\\..\\examples\\fillspill_example\\input\\rtcParameterConfig.xml
    :language: xml
    :lines: 12-17


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

The results of the simulation run can be seen in the plot below.

.. raw:: html
    :file: figures\\final_results_fillspill.html
