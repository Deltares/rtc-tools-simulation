model Reservoir
  type FlowRatePerArea = Real(unit = "mm/hour");
  import SI = Modelica.SIunits;

  // Parameters
  parameter SI.Length H_crest();
  parameter SI.Area max_reservoir_area() = 0;

  // Inputs
  // The fixed argument is necessary for defining optimization problems.
  input SI.Length H_observed(fixed=true);
  input SI.VolumeFlowRate Q_in(fixed=true);
  input SI.VolumeFlowRate Q_turbine(fixed=false);
  input SI.VolumeFlowRate Q_sluice(fixed=false);
  input SI.VolumeFlowRate Q_out_from_input(fixed=false);
  input Boolean do_spill(fixed=true);
  input Boolean do_pass(fixed=true);
  input Boolean do_poolq(fixed=true);
  input Boolean do_set_q_out(fixed=true);
  input Boolean use_composite_q(fixed=true);
  input Boolean compute_v(fixed=true);
  input Boolean include_evaporation(fixed=true);
  input Boolean include_rain(fixed=true);
  input FlowRatePerArea mm_evaporation_per_hour(fixed=true);
  input FlowRatePerArea mm_rain_per_hour(fixed=true);
  input Integer day(fixed=true);

  // Outputs/Intermediates
  output SI.Volume V();
  SI.Volume V_observed();
  output SI.VolumeFlowRate Q_out();
  output SI.VolumeFlowRate Q_out_corrected();
  output SI.VolumeFlowRate Q_error();
  SI.VolumeFlowRate Q_out_from_lookup_table();
  output SI.Length H();
  output SI.VolumeFlowRate Q_evap();
  output SI.VolumeFlowRate Q_rain();
  SI.Area Area();
  SI.VolumeFlowRate Q_spill_from_lookup_table();
  output SI.VolumeFlowRate Q_spill();

equation
  // Lookup tables:
  // V -> Area
  // V -> H
  // H -> QSpill_from_lookup_table
  // V -> QOut (when do_poolq)

  // Q_error defined as the difference in precalculated Q_out and the observed Volume change,
  // needed for ADJUST function
  Q_error = (compute_v - 1) * ((Q_in - Q_out) - der(V));

  // compute_v is a Boolean that calculates Q_out physics-based if 1, and observation-based when 0
  compute_v * (der(V) - (Q_in - Q_out + Q_rain - Q_evap)) + (1 - compute_v) * (V - V_observed) = 0;

  Q_evap = Area * mm_evaporation_per_hour / 3600 / 1000 * include_evaporation;
  Q_rain = max_reservoir_area * mm_rain_per_hour / 3600 / 1000 * include_rain;

  Q_spill = do_spill * Q_spill_from_lookup_table;

  Q_out = (
    do_pass * Q_in
    + do_poolq * Q_out_from_lookup_table
    + use_composite_q * (Q_turbine + Q_spill + Q_sluice)
    + do_set_q_out * Q_out_from_input
  );

  // This equation creates a 'bookkeeping' variable that closes the mass-balance when compute_v = 0
  Q_out_corrected = Q_out -  Q_error;

end Reservoir;
