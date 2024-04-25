Reservoir
=========
Contents:
    Doc Set_Q:

    Situation: We have had a look at the forecast that was carried out yesterday.
    We noticed a large difference between 12:00 and 15:00 between simulation and observation.
    Reservoir operation happened differently then we have accounted for in our rules, and some manual changes were probably carried out.
    We want to see what happens when the same unexpected discharge occurs today.
    We code: if 12 =< t =< 15 : set_q('Q_out', 'Q_obs_yesterday')

    Doc ADJUST:
    In this scenario, we consider a simulation run that starts a while before the current time.
    The simulation needs to extend past t = t0 to create a forecast.
    This set up is often used when there is suspicion of a discrepancy between observed and simulated behaviour.
    We recognize a bias in the timesteps before t = t0, so we want to take that into account.
    Scenario 1 (set_q): We can adjust the volume (and therefore h) to be equal to observations at t = t0. We continue with the simulation from that cold state.
    Scenario 2 (adjust): We apply set_q at t0, but also extrapolate the error in net discharge from the run-up period onto the forecast period. This applies a bias correction.


