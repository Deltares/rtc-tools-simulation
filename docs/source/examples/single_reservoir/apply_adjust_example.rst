.. _examples-single-reservoir-adjustexample:

``apply_adjust`` Scheme Example
==================================

This example shows how to use the :py:meth:`.ReservoirModel.apply_adjust` scheme when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``. 
There are observed elevations for the first portion of timesteps (until 13th of June). At these times, the simulation should
be adjusted based upon these observed values. Hence the outflow from the reservoir will be corrected to prevent diverging
water balances between simulation and observation. At times without elevation observations, reservoir outflow should be 0.4 m3/s.

The :py:meth:`.ReservoirModel.apply_adjust` scheme can be applied to model these operations. 

Main Model (python) File
------------------------

An example of the main model file `adjust_example.py` is given below.

.. literalinclude:: ../../../../examples/adjust_example/adjust_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/adjust_example/adjust_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/adjust_example/adjust_example.py
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
:py:meth:`.ReservoirModel.apply_adjust`.
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

The :py:meth:`.ReservoirModel.set_q` scheme is applied to set reservoir outflow to 0.4 m3/s.
The :py:meth:`.ReservoirModel.apply_adjust` scheme is then applied to correct for elevation observations 
when they are supplied to the model.

Lookup tables
-------------

This model uses only the standard lookup table ``h_from_v``, for other lookup tables, defaults from the generated template files can be used. 
Lookup table ``h_from_v`` is also used to convert the observed elevations (``H_observed``) into observed volumes.

This model also contains extraction of minimum and maximum values from the provided lookup tables. This is done by using the function 
:py:meth:`.get_lookup_tables_bounds_from_csv` (see :ref:`look-up-tables`). This function returns a dictionary which for each lookup table, stores the min 
and max values for each variable. In this example we add some of these to the logger. This results in the following messages:

  *INFO Volumes in the lookup table 'h_from_v' are in the range [0, 180636966]*

  *INFO Elevations in the lookup table 'v_from_h' are in the range [1542.306754, 1606.315533]*

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

The :py:meth:`.ReservoirModel.apply_adjust` scheme requires observed elevation data supplied via the ``timeseries_import.xml``

.. literalinclude:: ../../../../examples/adjust_example/input/timeseries_import.xml
    :language: xml
    :lines: 4-23

This additional input data is mapped to the internal variable, ``H_observed``, using the ``rtcDataConfig.xml``.

.. literalinclude:: ../../../../examples/adjust_example/input/rtcDataConfig.xml
    :language: xml
    :lines: 5-11

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

The results of the simulation run can be seen in the plot below. Observed (constant) elevations are provided for the initial
time period. 

By choosing `Show results from previous run`, results are shown without the :py:meth:`.ReservoirModel.apply_adjust` scheme.
It can be seen that in this case the simulated elevations differ from observations.

.. raw:: html
    :file: figures/final_results_adjust.html
