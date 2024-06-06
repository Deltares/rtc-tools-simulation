.. _examples-single-reservoir-adjustexample:

``apply_adjust`` Scheme Example
==================================

This example shows how to use the :py:meth:`.ReservoirModel.apply_adjust` scheme when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``. 
There are observed volumes for the first portion of timesteps (until 13th of June). At these times, the simulation should
be adjusted based upon these observed values. Hence the outflow from the reservoir will be corrected to prevent diverging
water balances between simulation and observation. At times without volume observations, reservoir outflow should be 0.4 m3/s.

The :py:meth:`.ReservoirModel.apply_adjust` scheme can be applied to model these operations. 
An additional output variable ``Q_out_corrected`` describes the corrected outflow based upon the observed volumes. 

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
The :py:meth:`.ReservoirModel.apply_adjust` scheme is then applied to correct for volume observations 
when they are supplied to the model.

The last lines

.. literalinclude:: ../../../../examples/adjust_example/adjust_example.py
  :language: python
  :start-at: # Create and run the model.

create and run a :py:class:`.SingleReservoir` model.
To run the model, we can run ``python adjust_example.py`` from the command line.


Lookup tables
-------------

This model uses only the standard lookup table ``h_from_v``, for other lookup tables, defaults from the generated template files can be used. 

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

The :py:meth:`.ReservoirModel.apply_adjust` scheme requires observed volume data supplied via the ``timeseries_import.xml``

.. literalinclude:: ..\\..\\..\\..\\examples\\adjust_example\\input\\timeseries_import.xml
    :language: xml
    :lines: 20-44

This additional input data is mapped to the internal variable, ``V_observed``, using the ``rtcDataConfig.xml``.

.. literalinclude:: ..\\..\\..\\..\\examples\\adjust_example\\input\\rtcDataConfig.xml
    :language: xml
    :lines: 11-16

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

The results of the simulation run can be seen in the plot below. Observed (constant) volumes are provided for the initial
time period, note that this leads to a non-zero ``Q_out_corrected``. 

By choosing `Show results from previous run`, results are shown without the :py:meth:`.ReservoirModel.apply_adjust` scheme.
It can be seen that in this case the simulated volumes differ from observations, and ``Q_out_corrected`` is equal to ``Q_out``.

.. raw:: html
    :file: figures\\final_results_adjust.html
