.. _examples-single-reservoir-rulecurveexample:

``apply_rulecurve`` Scheme Example
==================================

This example shows how to use the :py:meth:`.ReservoirModel.apply_rulecurve` scheme when modelling a single reservoir model.

.. note::

      For details about the full model file structure please see :ref:`examples-single-reservoir-basic`.

We consider a reservoir with a single inflow, ``Q_in``, and an outflow ``Q_out``. ``Q_out`` is comprised of a single component, 
a turbine, ``Q_turbine``.
The reservoir outflow should be determined to achieve the rulecurve (elevation of 1600m).
The rulecurve elevation should be achieved in single timestep with a maximum outflow of 10m3/s.

The :py:meth:`.ReservoirModel.apply_rulecurve` scheme can be applied to model these operations. 

Main Model (python) File
------------------------

An example of the main model file `rulecurve_example.py` is given below.

.. literalinclude:: ../../../../examples/rulecurve_example/rulecurve_example.py
  :language: python
  :lineno-match:

The template file mentioned in the :ref:`examples-single-reservoir-basic` will look very similar to this file,
except that the :py:meth:`apply_schemes` method still needs to be filled out.

The line

.. literalinclude:: ../../../../examples/rulecurve_example/rulecurve_example.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/rulecurve_example/rulecurve_example.py
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
:py:meth:`.ReservoirModel.apply_rulecurve`.
An overview of all available :py:class:`.ReservoirModel` methods
can be found in :ref:`reservoir-api`.

The :py:meth:`.ReservoirModel.apply_rulecurve` scheme is then applied to set the reservoir outflow through the turbine.
It will aim to match the simulated elevation to the provided rule curve. There are functions provided that
can alter the originally provided rule curve to account for differences with observations (e.g. during a
very dry year, or after some maintenance project). This will need to be computed before model simulation.

In the method :py:meth:`.ReservoirModel.pre` functions are called that accomplish certain pre-processing objectives.
In this model, we compute the deviation of the observed elevations to the provided rule curve. Based on these deviations,
the original rule curve is adjusted. In this case, we take the latest known deviation and apply that to all timesteps
after the end of ``H_observed``. There is also functionality to provide an application time, average deviations over a
moving window, or extrapolate the deviations linearly after the application time.


Lookup tables
-------------

The :py:meth:`.ReservoirModel.apply_rulecurve` scheme uses a lookup table ``v_from_h``. This  uses the same
data as the ``h_from_v`` lookup table, the data mapping can be achieved in the ``lookup_tables.csv`` file.

.. csv-table:: <base_dir>/lookup_tables/lookup_tables.csv
  :file: ../../../../examples/rulecurve_example/lookup_tables/lookup_tables.csv
  :header-rows: 1

This model also uses the standard lookup table ``h_from_v``.
For other lookup tables, defaults from the generated template files can be used. 

.. note::

      For further details about the lookup tables please see :ref:`examples-single-reservoir-basic`.

Input Data Files
----------------

The :py:meth:`.ReservoirModel.apply_rulecurve` scheme requires the following parameters from the ``rtcParameterConfig.xml`` file.
``Reservoir_Qmax``, upper limiting discharge while blending pool elevation (m^3), and
``rule_curve_blend``, the factor by which to reduce the current reservoir volume difference that will be mapped to the discharge this timestep.
``rule_curve_blend`` > 1 will cause the elevation to converge to the rule curve over time, but not match it. In this case (blend = 1)
it aims to match the rule_curve elevation at each timestep

These parameters are supplied to the model via the ``rtcParameterConfig.xml`` input file.

.. literalinclude:: ..\\..\\..\\..\\examples\\rulecurve_example\\input\\rtcParameterConfig.xml
    :language: xml
    :lines: 12-17

The scheme also requires an additional input timeseries, ``rulecurve``. This data is provided in the ``timeseries_import.xml``.

.. literalinclude:: ..\\..\\..\\..\\examples\\rulecurve_example\\input\\timeseries_import.xml
    :language: xml
    :lines: 1508-1538

The data is mapped to the variable, ``rulecurve`` via the ``rtcDataConfig.xml``.

.. literalinclude:: ..\\..\\..\\..\\examples\\rulecurve_example\\input\\rtcDataConfig.xml
    :language: xml
    :lines: 5-10

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
    :file: figures\\final_results_rulecurve.html
