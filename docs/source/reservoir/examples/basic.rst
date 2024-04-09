Basic Reservoir
===============

This example shows how to build a simple reservoir model.

File Structure
--------------

The file structure looks as follows::

  <base_dir>
  │   <model_file>.py
  ├───input
  │   ├───initial_state.csv
  │   ├───parameters.csv
  │   ├───(plot_table.csv)
  │   └───timeseries_import.csv
  └───lookup_tables
      ├───lookup_tables.csv
      ├───(data1.csv)
      ├───(data2.csv)
      └───(data3.csv)

..
    File structure was generated with the help of `tree /f <path_to_dir>` in terminal.

The `<base_dir>` is the base directory that contains all files to run the model.
It consists of the following files and folders.

* `<model_file>.py`: main model file that describes all the schemes for controlling
  the reservoir flow.

* `input`: directory containing all parameters and external input data.

  * `initial_state.csv`: file that contains the intial values.
  * `parameters.csv`: file that contains the model parameters.
  * `plot_table.csv` (optional): file that describes how the output should be visualised.
  * `timeseries_import.csv`: file with all input timeseries.

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
except that the :py:meth:`apply_schemes` method still needs to be filled out.

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

The method :py:meth:`apply_schemes` is called every timestep and contains the logic for
which schemes are applied.
The first argument ``self`` is the :py:class:`SingleReservoir` object itself.
Since :py:class:`SingleReservoir` inherits from :py:class:`ReservoirModel`,
``self`` can call any of the :py:class:`ReservoirModel` methods, such as
:py:meth:`get_current_datetime`,
:py:meth:`get_var`,
:py:meth:`set_q`,
:py:meth:`apply_spillway`.
An overview of all available :py:class:`ReservoirModel` methods
can be found in :ref:`reservoir-api`.

In this example, the :py:meth:`apply_schemes` method starts by checking
if the elevation ``H`` is higher than the crest elevation ``H_crest``.
If this is the case, and the current month is in between April and September,
the outflow is set by :py:meth:`set_q`.
Otherwise, the spillway scheme is applied.
If the elevation is below the crest elevation, the outflow is set by :py:meth:`set_q`.

The last lines

.. literalinclude:: ../../../../examples/single_reservoir/single_reservoir.py
  :language: python
  :start-at: # Create and run the model.

create and run a :py:class:`SingleReservor` model.
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

  Storage_m3,Elevation_m
  0,1542.306754
  13439700,1562.118995
  16152300,1563.643014
  21700800,1566.691051
  "...","..."
