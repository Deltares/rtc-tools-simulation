.. _getting-started:

Getting Started
+++++++++++++++

Installation
============

Python 3.9 is recommended for running RTC-Tools.

For most users, the easiest way to install RTC-Tools
is using the `pip <https://pip.pypa.io/>`_ package manager.

Using the Pip Package Manager
-----------------------------

Although not required, it is recommended to install RTC-Tools in a virtual environment.
See the `official Python tutorial <https://docs.python.org/3/tutorial/venv.html>`_
for more information on how to set up and activate a virtual environment.

RTC-Tools-Simulation, including its dependencies,
can be installed using the `pip <https://pip.pypa.io/>`_ package manager.
From the command line, run:

.. code-block:: bash

  pip install rtc-tools-simulation

Single Reservoir Modelling
==========================

Examples of how to model a single reservoir can be found in :ref:`examples-single-reservoir`.
First take a look at :ref:`examples-single-reservoir-basic`.
This example includes a description of the file structure, auto-generation of template files,
and configuring look-up tables.

Other examples within :ref:`examples-single-reservoir`
showcase different schemes that can be applied.

The schemes that can be applied to a single reservoir are documented in :ref:`reservoir-api`.
Additionally, details of the underlying Modelica model
can be found in :ref:`single-reservoir-model`.

Lookup Tables
=============

Details of how to create lookup tables can be found in :ref:`look-up-tables`.
