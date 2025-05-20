.. _template-generation:

Template Generation
===================

Using the command ``rtc-tools-reservoir-template -d <base_dir> -n <reservoir_name>``
from the command line will create a directory `<base_dir>` with template files
for a reservoir model called `<reservoir_name>`.
The directory `<base_dir>` will be created in the current working directory
and will contain a file structure as described above.
The generated source file and data files are all template files
that need to be completed by the user.

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