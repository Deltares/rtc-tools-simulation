.. _examples-single-reservoir-basic:

Basic Single Reservoir
======================

This example shows how to build a simple single reservoir model.

File Structure
--------------

The file structure looks as follows::

  <base_dir>
  │   <model_file>.py
  ├───input
  │   ├───(plot_table.csv)
  │   └───rtcDataConfig.xml
  │   └───rtcParameterConfig.xml
  │   └───timeseries_import.xml
  ├───lookup_tables
  │   ├───lookup_tables.csv
  │   ├───(<data1>.csv)
  │   ├───(<data2>.csv)
  │   └───(<data3>.csv)
  └───output

..
    File structure was generated with the help of `tree /f <path_to_dir>` in terminal.

The `<base_dir>` is the base directory that contains all files to run the model.
It consists of the following files and folders.

* `<model_file>.py`: main model file that describes all the schemes for controlling
  the reservoir flow.

* `input`: directory containing all parameters and external input data.

  * `plot_table.csv` (optional): file that describes how the output should be visualised.
  * `rtcParameterConfig.xml`: file that contains the model parameters.
  * `timeseries_import.xml`: file with all input timeseries and initial conditions.
  * `rtcDataConfig.xml`: file that contains the mappings for input/output timeseries (from FEWS) and internal model variables.

* `lookup_tables`: directory that contains all data for lookup tables.

  * `lookup_tables.csv`: file that describes all lookup tables.
  * `***.csv`: data files that contain data for generating lookup tables.

Each of these files will be described in more detail in the following sections.

Creating Template Files
-----------------------

Using the command ``rtc-tools-reservoir-template -d <base_dir> -n <reservoir_name>``
from the command line will create a directory `<base_dir>` with template files
for a reservoir model called `<reservoir_name>`.
The directory `<base_dir>` will be created in the current working directory
and will contain a file structure as described above.
The generated source file and data files are all template files
that need to be completed by the user.

Main Model File
---------------

An example of the main model file `<model_file>.py` is given below.

.. literalinclude:: ../../../../examples/single_reservoir/single_reservoir.py
  :language: python
  :lineno-match:

The template file mentioned in the previous section will look very similar to this file,
except that the :py:meth:`.apply_schemes` method still needs to be filled out, and the optional ``def``, 
:py:meth:`.calculate_output_variables`, is not added..

The line

.. literalinclude:: ../../../../examples/single_reservoir/single_reservoir.py
  :language: python
  :start-at: CONFIG
  :end-at: CONFIG

sets the model configuration.
This model configuration is defined by the base directory ``base_dir``.
In most cases, the base directory is ``Path(__file__).parent``,
which is the directory of the current file.

The line

.. literalinclude:: ../../../../examples/single_reservoir/single_reservoir.py
  :language: python
  :start-at: class
  :end-at: class

defines a class :py:class:`SingleReservoir`
that inherits all properties and functionalities
of the predefined class :py:class:`ReservoirModel`.
An overview of this class can be found in :ref:`reservoir-api`
and details of the underlying model it uses can be found in :ref:`single-reservoir-model`.

The method :py:meth:`apply_schemes` is called every timestep and contains the logic
for which schemes are applied.
The first argument ``self`` is the :py:class:`SingleReservoir` object itself.
Since :py:class:`SingleReservoir` inherits from :py:class:`ReservoirModel`,
``self`` can call any of the :py:class:`ReservoirModel` methods, such as
:py:meth:`get_current_datetime`,
:py:meth:`get_var`,
:py:meth:`set_q`,
:py:meth:`apply_spillway`.
An overview of all available :py:class:`ReservoirModel` methods
can be found in :ref:`reservoir-api`.

In this example, the :py:meth:`apply_schemes` method starts
by including rain and rain evaporation by calling ``self.include_rainevap()``.
Since :py:meth:`apply_schemes` is applied at each time step,
this means rain and evaporation is included at each time step.
The method then checks if the elevation ``H`` is higher than the crest elevation ``H_crest``.
If this is the case, and the current month is in between April and September,
the outflow is set by :py:meth:`set_q`.
Otherwise, the spillway scheme is applied.
If the elevation is below the crest elevation, the outflow is set by :py:meth:`set_q`.

The last line

.. literalinclude:: ../../../../examples/single_reservoir/single_reservoir.py
  :language: python
  :start-at: # Create and run the model.

runs a :py:class:`SingleReservoir` model.
To run the model, we can run ``python <model_file>.py`` from the command line.


Lookup tables
-------------

Lookup tables are used to define relations between volume, elevation, surface area, and outflow.
They are defined in the `<base_dir>/lookup_tables` folder.
A description of all lookup tables is given in the `lookup_tables.csv` file.
In this example, this file looks as follows.

.. csv-table:: <base_dir>/lookup_tables/lookup_tables.csv
  :file: ../../../../examples/single_reservoir/lookup_tables/lookup_tables.csv
  :header-rows: 1

It consists of the following columns.

* `name`: name of the lookup_table.
  The default reservoir model uses the lookup tables
  `h_from_v`, `area_from_v`, and `qspill_from_h`.

* `data`: data file used to create the lookup table.
  This should a csv file where all fields are seperated by a ``,``.

* `var_in`: input variable for creating the lookup table.
  This should be one of the columns in the data file.

* `var_out`: output variable for creating the lookup table.
  This should be one of the columns in the data file.

A data file, such as `v_h.csv`, looks as follows.

.. csv-table:: <base_dir>/lookup_tables/v_h.csv
  :header-rows: 1

  volume_m3,height_m
  0,1542.306754
  13439700,1562.118995
  16152300,1563.643014
  21700800,1566.691051
  "...","..."

When setting up the model, the model object will look for the following lookup tables:

* h_from_v
* area_from_v
* qout_from_v
* qspill_from_h

It is therefore important to use these same names in the `lookup_tables.csv` file.

Input Data Files
----------------

The input folder contains a configuration file `rtcDataConfig.xml`
a parameter file `rtcParameterConfig.xml`,
and an input data file `timeseries_import.xml`.

The `rtcDataConfig.xml` file contains a mapping between external data and internal model variables.
In this example, `rtcParameterConfig.xml` looks as follows.

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <rtcDataConfig xmlns="http://www.wldelft.nl/fews" xmlns:rtc="http://www.wldelft.nl/fews" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.wldelft.nl/fews ../xsd/rtcDataConfig.xsd">
    <timeSeries id="V">
      <PITimeSeries>
        <locationId>reservoir</locationId>
        <parameterId>V</parameterId>
      </PITimeSeries>
    </timeSeries>
    ...
  </rtcDataConfig>

.. .. literalinclude:: ..\\..\\..\\..\\examples\\single_reservoir\\input\\rtcDataConfig.xml
..     :language: xml
..     :lines: 12-17

The line ``<timeSeries id=V>`` indicates that the model variable is called ``V``
and the lines ``<locationId>reservoir</locationId>`` and ``<parameterId>V</parameterId>``
indicate that ``V`` has locationId ``resrvoir`` and parameterId ``V``.
The locationId and parameterId are used to label data in data files
such as the input file `timeseries_import.xml` or the output file `timeseries_export.xml`.

The input file `timeseries_import.xml` is usually not created by the user,
but generated by a FEWS application.
In this example, the input file contains the following lines.

.. literalinclude:: ../../../../examples/single_reservoir/input/timeseries_import.xml
    :language: xml
    :lines: 4-19

The line ``<event date="2022-06-07" time="06:00:00" value="136500000" flag="8"/>``
sets the value of ``V`` at the initial time (2022-06-07, 06:00:00).
We only provide the reservoir volume ``V`` with an initial value
and therefore there is only one ``event`` block.
If we want to set a variable at each time step, like the inflow ``Q_in``,
we have an ``event`` block for each time step.

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
    :file: figures/final_results_basic.html