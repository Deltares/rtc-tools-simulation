.. _examples-single-reservoir-spillwayexample:

``apply_spillway`` Scheme Example
=================================

This example shows how to use the :py:meth:`.ReservoirModel.apply_spillway` scheme when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``. ``Q_out`` is comprised of two components, 
a spillway, ``Q_spill``, and a turbine ``Q_turbine``.
The reservoir outflow is determined based upon the reservoir elevation, ``H``, at each timestep.

.. math::
    Q_{out} = Q_{turbine}+Q_{spill}\\

    Q_{spill} = 
      \begin{cases}
        Q_{spill}(H) & \text{if $H > H_{crest}$}\\
        0 & \text{otherwise}\\
      \end{cases}\\

    Q_{turbine} = 
      \begin{cases}
        0.6 & \text{if $H > H_{crest}$}\\
        0.4 & \text{otherwise}\\
      \end{cases}


The :py:meth:`.ReservoirModel.apply_spillway` and :py:meth:`.ReservoirModel.set_q` schemes can be applied to model these operations. 

Main Model (python) File
------------------------

An example of the main model file `spillway_example.py` is given below.

.. literalinclude:: ../../../../examples/spillway_example/spillway_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/spillway_example/spillway_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/spillway_example/spillway_example.py
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
:py:meth:`.ReservoirModel.get_var`,
:py:meth:`.ReservoirModel.set_q`, and :py:meth:`.ReservoirModel.apply_spillway`,
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

In this example, the :py:meth:`.ReservoirModel.apply_schemes` method starts
by collecting the current reservoir elevation as this is used to determine operations. 
The method then checks if the elevation, ``H``, is higher than the crest level.
The crest level is supplied to the model via the ``rtcParameterConfig.xml`` input file.
The ``set_q`` or ``apply_spillway`` scheme is then applied to set the reservoir
outflow through the spillway or turbine.

Lookup tables
-------------

This model uses the standard lookup tables ``h_from_v``.

The :py:meth:`.ReservoirModel.apply_spillway` scheme ensures that the spill, ``Q_spill``,
is computed from the elevation, ``H``, using a lookuptable ``qspill_from_h``.

This file, ``h_qspill.csv`` looks as follows,

.. csv-table:: <base_dir>/lookup_tables/h_qspill.csv
  :file: ../../../../examples/spillway_example/lookup_tables/h_qspill.csv
  :header-rows: 1

This file is mapped to the internal ``qspill_from_h`` table via the ``lookup_tables.csv`` file

.. csv-table:: <base_dir>/lookup_tables/lookup_tables.csv
  :file: ../../../../examples/spillway_example/lookup_tables/lookup_tables.csv
  :header-rows: 1

For other lookup tables, defaults from the generated template files can be used. 

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

The crest level is supplied to the model via the ``rtcParameterConfig.xml`` input file.

.. literalinclude:: ../../../../examples/spillway_example/input/rtcParameterConfig.xml
    :language: xml
    :lines: 6-8

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

The results of the simulation run can be seen in the plot below.

.. raw:: html
    :file: figures/final_results_spillway.html
