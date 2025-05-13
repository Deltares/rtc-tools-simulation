.. _examples-single-reservoir-suminf-floodflag-example:

``suminf`` and ``floodflag`` Utilities Example
==============================================

This example shows how to use the :py:meth:`.ReservoirModel.calculate_cumulative_inflows` and :py:meth:`.ReservoirModel.get_flood_flag` 
Utilities when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``. 


Main Model (python) File
------------------------

An example of the main model file `suminf_floodflag_example.py` is given below.

.. literalinclude:: ../../../../examples/suminf_floodflag_example/suminf_floodflag_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`.ReservoirModel.apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/suminf_floodflag_example/suminf_floodflag_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/suminf_floodflag_example/suminf_floodflag_example.py
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

The :py:meth:`.ReservoirModel.set_q` scheme is applied to set reservoir outflow to 1.0 m3/s (the ``q_out_daily_average``).

Lookup tables
-------------

This model uses only the standard lookup table ``h_from_v``, for other lookup tables, defaults from the generated template files can be used. 
Lookup table ``h_from_v`` is also used to convert the observed/initial elevations (``H_observed``) into observed/initial volumes.

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

No special input is required when using these utilities.

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
The plot containts the cumulative inflow in a separate plot. 
The plot also shows the flood flag. This is set to one as, given the ``q_out_daily_average``,
within the pre-porcessing it is expected that the elevation ``H`` will exceed the flood level ``flood_elevation`` at some point during the simulatiom.

Within :py:meth:`.ReservoirModel.apply_schemes`, :py:meth:`.ReservoirModel.set_q` is used to set the outflow equal to ``q_out_daily_average``.
Hence the plots also show the elevation, ``H`` rising above ``flood_elevation``.

.. raw:: html
    :file: figures/final_results_suminf_floodflag.html
