.. _examples-single-reservoir-minqxample:

``apply_minq`` Scheme Example
=================================

This example shows how to use the :py:meth:`.ReservoirModel.apply_minq` scheme
when modelling a single reservoir model.

.. note::

    For details about the full model file structure
    please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``. 
The outflow is determined in such a way that the peak outflow is minimum
while making sure that the elevation remains within given bounds.

The :py:meth:`.ReservoirModel.apply_minq` scheme
can be applied to calculate an optimal outflow and apply it to the simuatlion. 

Main Model (python) File
------------------------

An example of the main model file `minq_example.py` is given below.

.. literalinclude:: ../../../../examples/minq_example/minq_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/minq_example/minq_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/minq_example/minq_example.py
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
``self`` can call any of the :py:class:`.ReservoirModel` methods,
such as :py:meth:`.ReservoirModel.apply_minq`.
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

In this example, the :py:meth:`.ReservoirModel.apply_schemes` method
calls the ``apply_minq`` method.
If no optimal outflow has been calculated yet,
this method will calculate the optimal outflow (i.e. outflow with a minimal peak)
given upper bounds on the elevation (``h_min``, ``h_max``)
and a target elevation (``h_target``).
It will then use this optimized outflow to set the outflow of the simulation.
The upper and lower bounds for the elevation are set in this example to 0 and 40, respectively,
and the target elevation is set to the timeseries "rule_curve".
This timeseries is given via the ``timeseries_import.xml`` file.


Lookup tables
-------------

This model uses the standard lookup tables ``h_from_v``.

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

The "rule_curve" timeseries is supplied to the model via the ``timeseries_import.xml`` input file.

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
    :file: figures\\final_results_minq.html
