.. _initial-conditions:

Calculation of the dispersion discharge using the UNESCO formulation
====================================================================

This equation defines the effective gravity (:math:`\rho'`) between two fluid layers of different densities (:math:`\rho_1` and :math:`\rho_2`),
it quantifies how strongly the density difference drives internal motion between the layers.:

.. math::

   \rho' = g \frac{\lvert \rho_1 - \rho_2 \rvert}{\tfrac{\rho_1 + \rho_2}{2}}
   \tag{1}

where (:math:`g` is the acceleration of gravity.
From the effective gravity the internal wave celerity (:math:`c_w`) is calculated, 
the speed of a two-layer internal wave (or disturbance) at the interface:

.. math::

   c_w = 0.5 \sqrt{\rho' \, \min(H_1, H_2)}
   \tag{2}

where :math:`H_1` and :math:`H_2` are the depth of the two layers/reservoirs/boxes at the interface.
Finally, the dispersion discharge is calculated. This equation gives the volumetric
exchange between two connected layers driven by dispersion.

.. math::

   Q_1 = 0.5 \, c_w \, \min(B_1, B_2) \, \min(H_1, H_2)
   \tag{3}

where :math:`B_1` and :math:`B_2` are the width of the two layers/reservoirs/boxes at the interface.
Substituting back the effective gravity and further simplifying it,
we get the following expression for dispersion discharge:

.. math::

   Q_1 = \tfrac{1}{4}
         \sqrt{
           g \frac{\lvert \rho_1 - \rho_2 \rvert}{\tfrac{\rho_1 + \rho_2}{2}}
         }
         \, \min(B_1, B_2) \, \min(H_1, H_2)^{1.5}
   \tag{4}

.. math::

   Q_1 = \tfrac{1}{4} \sqrt{2g}
         \sqrt{
           \frac{\lvert \rho_1 - \rho_2 \rvert}{\rho_1 + \rho_2}
         }
         \, \min(B_1, B_2) \, \min(H_1, H_2)^{1.5}
   \tag{5}

The densities are calculated using the salinity-density relations.


Salinity–Density Relations
--------------------------

First, the salinity :math:`S` in psu is calculated from the density and concenration :math:`C`.

.. math::
   
   S = \frac{1000\,C}{\rho}
   \tag{6}

The density can be expressed also from reference densities for different temperatures and a reference density,
this approximates the UNESCO seawater equation of state using a polynomial in salinity.:

.. math::

   \rho =
     \rho_{\mathrm{ref}}
     + a S
     + b S^{1/2}
     + c S^{2}
   \tag{8}

.. math::

   \rho =
     \rho_{\mathrm{ref}}
     + a \frac{1000C}{\rho}
     + b \frac{31.622 \, C^{1/2}}{\rho^{1/2}}
     + c \frac{C^{2}}{\rho^{2}} 10^{4}
   \tag{9}

The constants :math:`a`, :math:`b`, :math:`c` and the refernece denisty :math:`\rho_{ref}` depend on the temperature:


The temperature–dependent coefficients for the upper layer are:

.. math::

   a =
     8.24493 \times 10^{-1}
     - 4.0899 \times 10^{-3} \, T
     + 7.6438 \times 10^{-5} \, T^{2}

.. math::

   b =
     -5.72466 \times 10^{-3}
     + 1.0227 \times 10^{-4} \, T
     - 1.6546 \times 10^{-6} \, T^{2}

.. math::

   c = 4.8314 \times 10^{-4}

.. math::

   \rho_{\mathrm{ref}} = {} &
     999.842594
     + 6.793952 \times 10^{-2} \, T
     - 9.095290 \times 10^{-3} \, T^{2} \\
     & {}+ 1.001685 \times 10^{-4} \, T^{3}
     - 1.120083 \times 10^{-6} \, T^{4}
     + 6.536332 \times 10^{-9} \, T^{5}



Note: in the calculation of :math:`a`, :math:`b`, :math:`c` there are higher order terms present.
We neglected these higher order terms. This impmlemented formulation was compared to the complete
equation is the range of temperatures and concentrations.
The difference between the original equation and the approximation was in the order of a decimal of density.   
