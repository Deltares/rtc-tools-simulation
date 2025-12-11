Modelling Salt
==============

This funtionality of RTC-Tools simulation to model salt is part of the
*Zout Transport Model*, *ZTM*. It can only be used together the Modelica
blocks that can be found in rtc-tools-channel-flow (version > 1.3). This can be installed apart, just like the rtc-tools-interface, that is needed to prepare figures.

We will further refer
to this functionality as *ZTM*.
 
ZTM solves both the advection and dispersion equations. First, the discharge flux is calculated using advection. The downstream discharge and intermediate fluxes are then determined such that either all water levels become equal (resulting in zero downstream discharge) or all water levels remain constant over time, with the downstream discharge adjusting accordingly to maintain this balance. 
 
Assumptions: 

* Concentrations cannot be exactly identical; an `\epsilon` tolerance determines how close they may be.
* The model has been tested with multiple boxes, but splitting one exchange into two (a Y-shaped branching) has not yet been tested.
* The model has been tested only with discharge in a single direction. Although flow reversal is possible, it has not yet been tested.

There are two possible ways to use the model. In the first approach, all inflows and outflows are specified, and the water levels adjust to accommodate the prescribed flows (“water_level_closing”). In the second approach, the water levels are kept constant, and the downstream discharge is used to close the system.

Currently, the model is designed to connect elements in a linear sequence and to include either an open or a closed boundary. The user can specify an open boundary by placing a boundary block, and can indicate whether the ZSF is connected to any of the boundaries.

Contents:

.. toctree::
  :maxdepth: 0

  salt/getting_started
  salt/modelling
  salt/dispersive
  salt/zsf
  salt/api
 


