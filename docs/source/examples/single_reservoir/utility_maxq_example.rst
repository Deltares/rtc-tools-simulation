.. _examples-single-reservoir-maxqexample:

``maxq`` Utility Example
========================

This example shows how to use the :py:meth:`.ReservoirModel.find_maxq` utility when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and both spillway and turbine discharges.
The reservoir outflow is determined based upon the reservoir elevation, ``H``, at each timestep.
The utility aims to compute the maximum possible release based on the current reservoir elevation.
It can consider 3 different options, a fixed maximum discharge (``Fixed``), a fixed maximum discharge plus
Q/H spillway relation (``Spillway``) and a option where the downstream tailwater discharge relation is taken
into account (``Tailwater``).

Main Model (python) File
------------------------

An example of the main model file `maxq_example.py` is given below.

.. literalinclude:: ../../../../examples/maxq_example/maxq_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/maxq_example/maxq_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/maxq_example/maxq_example.py
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
:py:meth:`.ReservoirModel.get_var` and
:py:meth:`.ReservoirModel.find_maxq`.
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

In this example, the :py:meth:`.ReservoirModel.apply_schemes` method starts
by collecting the current model timestep, since the utility only works for timesteps after the first.
The :py:meth:`.ReservoirModel.find_maxq` utility is then applied to compute the hypothetical maximum release using the 3 different cases.

Lookup tables
-------------

This model uses a variety of lookup tables, which are all defined in the file ``lookup_tables.csv``.

.. literalinclude:: ../../../../examples/maxq_example/lookup_tables/lookup_tables.csv
  :language: python

The required lookup_tables depend on the option that is chosen.

* For ``Fixed``, none are required.
* For ``Spillway``, the Q/H relationship of the spillway is required to be passed in a lookup_table 
  named ``qspill_from_h``.
* For option ``Tailwater``, we also need the Q/H relationship downstream, as well as
  the Q/dh relationship of the turbine. The configurator needs to provide those through lookup_tables
  ``qtw_from_tw`` and ``qnotspill_from_dh`` respectively. Lastly, for ``Tailwater`` a optional variable ``solve_guess`` can
  be provided to guide the equilibrium solver in finding the final value. If nothing is passed, it defaults to the
  current reservoir elevation as an initial guess.

.. note::

      For details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

.. note::

      For details about input file structure please see :ref:`examples-single-reservoir-basic`.

Output Data
-----------

The results of the simulation will appear in the `output` folder
in a file called `timeseries_export.xml`.
The data is linked to model variables via the `rtcDataConfig.xml`
in the same way as with `timeseries_import.xml`.

Automatic Plotting
------------------

There is a `plot_table.csv` in the input folder.
This is used by the rtc-tools-interfaces module (automatically installed with this package)
to plot the model output, including the theoretical maximum discharges for each method.
For more details on how to use this file and visualize results,
see `RTC-Tools-Interface <https://gitlab.com/rtc-tools-project/rtc-tools-interface>`_.

The results of the simulation run can be seen in the plot below.

.. raw:: html
    :file: figures/final_results_maxq.html