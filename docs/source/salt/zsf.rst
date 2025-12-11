.. _zsf_connection:

Connection to ZSF (Sea Lock Formulation Model)
==============================================

`ZSF <https://libzsf.readthedocs.io/en/latest/index.html>`_ is a Deltares tool to calculate salt intrusion through shipping locks. ZTM has seamless connection to ZSF.


Calculations using ZSF and two concentration boundaries
-------------------------------------------------------

In this scenario there is upstream (sea) and downstream (lake) a ZSF model coupled. Make sure that the sea and lake concentrations give to ZSF (in the Pyhton file) are the same as the initial conditons given to the model (initial_state.csv: storage0.C is the sea and storage4.C is the lake).


There are four parameters that can be adjusted:
	


.. literalinclude:: ../../../../rtc-tools-simulation/examples/salt_transport/src/example_three_boxes_ZSF.py
  :language: python
  :lines: 46-47
  
.. literalinclude:: ../../../../rtc-tools-simulation/examples/salt_transport/src/example_three_boxes_ZSF.py
  :language: python
  :lines: 51-52  
  
The open boundary means that the boundary has an open connection to the sea / lake. The concentration of these water bodies can be given in initial_conditions.csv.
The phase-wise connection is not released yet.