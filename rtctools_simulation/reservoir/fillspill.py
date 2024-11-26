"""
Module to compute FILLSPILL functionality
------------------------------------
"""
import logging
import numpy as np

logger = logging.getLogger("rtctools")

def fillspill(self,
    inflow: float,
    qmin: float,
    qlim: float,
    hmax: float, 
    spill_type: str = 'CREST',
    qpassmax: float = np.inf,
) -> float:
    """
    Determines the outflow from the reservoir based on the inflow and minimum required 
    outflow (downstream water demands or power generation objectives), as well as reservoir
    characteristics of maximum discharge of the dam facilitied or operational rules 
    (e.g. maximum generator discharge, maximum sluice discharge).
    
    :param inflow: float
        Discharge into the reservoir at the current timestep [m^3/s].
    :param qmin: float
        Required minimum discharge [m^3/s].
    :param qlim: float
        Maximum discharge without spill [m^3/s]
    :param hmax: float
        Elevation at which spill starts to occur, either controlled by gated facilities or 
        uncontrolled across the crest. [m]
    :param spill_type: str
        Type of spill that occurs, either gated or crested
    :param qpassmax: float
        Maximum discharge that can be routed through the facilities of the structure, 
        without routing over the crest. If exceeded, the SPILLWAY function is activated. [m3/s]
        
    :return q_out: float
        The computed outflow for the current timestep [m^3/s].
    """
    current_h = self.get_var(var = 'H')

    if inflow <= qmin: ## Use storage to supply minimum outflow
        q_out = qmin
    elif inflow <= qlim: ## If inflow between qmin and qlim, pass it directly through the system
        q_out = inflow
    elif qlim < inflow: ## discharge qlim, excess is added to storage
        q_out = qlim
        if current_h > hmax: ## If stage exceeds hmax, and storage would increase, apply spill
            self.apply_spillway()


    self.set_q(
        target_variable="Q_turbine",
        input_type="parameter",
        input_data=q_out,
    )
    