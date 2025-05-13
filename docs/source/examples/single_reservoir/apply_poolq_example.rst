.. _examples-single-reservoir-poolqxample:

``apply_poolq`` Scheme Example
=================================

This example shows how to use the :py:meth:`.ReservoirModel.apply_poolq` scheme when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``.
The reservoir outflow should be determined by a lookup table.

The :py:meth:`.ReservoirModel.apply_poolq` scheme can be applied to model these operations. 

Main Model (python) File
------------------------

An example of the main model file `poolq_example.py` is given below.

.. literalinclude:: ../../../../examples/poolq_example/poolq_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/poolq_example/poolq_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/poolq_example/poolq_example.py
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
:py:meth:`.ReservoirModel.apply_poolq`.
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

In this example, the :py:meth:`.ReservoirModel.apply_poolq` scheme is then applied inside of
:py:meth:`.ReservoirModel.apply_schemes` to set the reservoir outflow.

Lookup tables
-------------

This model uses the standard lookup table ``h_from_v``.

Additionally, the reservoir outflow is determined by a lookup table with name ``qout_from_v``. It is possible to 
impose a day dependence on this lookup table to create a 2D lookup table. In this example, we consider a 
lookup table which is constant in time. Hence, the ``day`` column is constant. 

The input file, ``qout_v.csv`` looks as follows,

.. csv-table:: <base_dir>/lookup_tables/qout_v.csv
  :file: ../../../../examples/poolq_example/lookup_tables/qout_v.csv
  :header-rows: 1

This file is mapped to the internal ``qout_from_v`` table via the ``lookup_tables.csv`` file

.. csv-table:: <base_dir>/lookup_tables/lookup_tables.csv
  :file: ../../../../examples/poolq_example/lookup_tables/lookup_tables.csv
  :header-rows: 1

For other lookup tables, defaults from the generated template files can be used. 

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

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
    :file: figures/final_results_poolq.html
