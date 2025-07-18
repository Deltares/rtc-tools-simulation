.. _examples-single-reservoir-passflowexample:

``apply_passflow`` Scheme Example
=================================

This example shows how to use the :py:meth:`.ReservoirModel.apply_passflow` scheme when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``.
The reservoir outflow is determined based upon the day of the month at each timestep.

.. math::

    Q_{out} = 
      \begin{cases}
        Q_{in} & \text{from 12th to 19th of each month}\\
        Q_{out,target} & \text{otherwise}\\
      \end{cases}\\

    Q_{out,target} = \text{is a timeseries with values all 3$m^3/s$}

The :py:meth:`.ReservoirModel.apply_passflow` and :py:meth:`.ReservoirModel.set_q` schemes can be applied to model these operations. 

Main Model (python) File
------------------------

An example of the main model file `passflow_example.py` is given below.

.. literalinclude:: ../../../../examples/passflow_example/passflow_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/passflow_example/passflow_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/passflow_example/passflow_example.py
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
:py:meth:`.ReservoirModel.get_current_datetime`,
:py:meth:`.ReservoirModel.set_q`, and :py:meth:`.ReservoirModel.apply_passflow`,
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

In this example, the :py:meth:`.ReservoirModel.apply_schemes` method starts
by collecting the current timestep as this is used to determine operations. 
The method then checks if the current timestep is between the 12th and 19th of the month.
The ``set_q`` or ``apply_passflow`` scheme is then applied to set the reservoir
outflow.

Lookup tables
-------------

This model uses only the standard lookup table ``h_from_v``,
for other lookup tables, defaults from the generated template files can be used. 

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

This implementation of the :py:meth:`.ReservoirModel.set_q` scheme requires input data for the ``Q_out_target``, supplied via the ``timeseries_import.xml``

.. literalinclude:: ../../../../examples/passflow_example/input/timeseries_import.xml
    :language: xml
    :lines: 516-536

This additional input data is mapped to the variables, ``Q_out_target`` using the ``rtcDataConfig.xml``.

.. literalinclude:: ../../../../examples/passflow_example/input/rtcDataConfig.xml
    :language: xml
    :lines: 19-25

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
    :file: figures/final_results_passflow.html
