.. _examples-salt-transport-basic:

Basic Salt Transport Example
============================

This example shows how to use a simple model with salt transport.

Description of the example
--------------------------
The example shows three interconnected boxes that represent a lake. Between the boxes advective
and dispersive transport occurs. The upstream and downstream boundary can be open (connected to another
water body) or closed. In case of closed boundary by default there is zero discharge coming to the system.
The user can change it by setting values of storage1_qforcing_advective and storage1_mforcing_advective in the import file.

If dicharge closing is chosen, the downstream discharge is set such that the water level of 
all the three boxes stays constant. An initial concentration of the boxes can be given.

Running the model
-----------------
The model can be run by running the ``example_three_boxes_ZSF.py`` file. After the run 
the message should be ``Process finished with exit code 0`` and the output folder should contain
the files listed in the file tree abovel.

Inspecting the results
----------------------
The results can be seen either on the figure overall_results.png or on the final_results.html.
The overall_reslts figure is a built in figure by ZTM.


The final_results.html is created by rtc-tools-interface, and the variables to plot can be 
set through the file src/plot_table.csv


User settings
-------------
The user can set several options:

* the upstream or downstream the boundary is open (there is an open connection with the sea / lake)
* use ZSF: the model automtatically calls ZSF on the given boundary
* closing term: the model is set up such that the water level at every box stays the same. If water is 
  coming into the model, it should be either distributed evenly among the boxes (water level closing) or   
  it will be assigned to a downstream discharge term. This process is known as advective transport.

.. literalinclude:: ../../../../examples/salt_transport/src/example_three_boxes_ZSF.py
  :language: python
  :lines: 44-52