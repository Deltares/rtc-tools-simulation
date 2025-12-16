.. _getting-started:

Getting started
===============

This example shows how to use a model with advective and dispersive salt transport.

File Structure
--------------

The file structure looks as follows::

  <base_dir>
  ├───input
  │   ├───plot_table.csv
  │   ├───initial_state.csv
  │   └───timeseries_import.csv
  ├───model
  │   ├───ExampleThreeBoxesZSF.mo
  │   ├───ExampleThreeBoxesUpBndZSF.mo
  │   ├───ExampleThreeBoxesTwoBndZSF.mo
  │   └───ExampleThreeBoxesUpBndZSF.mo
  ├───src
  │   └───example_three_boxes_ZSF.py
  └───output
      ├───overall_results.png
      ├───timeseries_export.csv
      ├───cached_results
      └───figures
	      └───final_results.html


Necessary packages
------------------
The following Python packages are needed to be able to run the model:

* rtc-tools
* rtc-tools-simulation
* rtc-tools-interface
* rtc-tool-channel-flow > 1.3
In case of connection to ZSF, you also need pyzsf.


