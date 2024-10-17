model Reservoir
  type FlowRatePerArea = Real(unit = "mm/hour");
  import SI = Modelica.SIunits;

  parameter SI.Length H_crest();
  parameter SI.Area max_reservoir_area() = 0;

  SI.Volume V_observed();
  input SI.Volume H_observed();
  input SI.VolumeFlowRate Q_in();
  input SI.VolumeFlowRate Q_turbine();
  input SI.VolumeFlowRate Q_sluice();
  input SI.VolumeFlowRate Q_out_from_input();
  input Boolean do_spill;
  input Boolean do_pass;
  input Boolean do_poolq;
  input Boolean compute_v;
  input Boolean include_evaporation;
  input Boolean include_rain;
  input Boolean do_set_q_out;
  input FlowRatePerArea mm_evaporation_per_hour();
  input FlowRatePerArea mm_rain_per_hour();
  input SI.Length rule_curve();
  input Integer day;

  output SI.Volume V();
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
    + (1 - do_pass) * (1 - do_poolq) * (1 - do_set_q_out) * (Q_turbine + Q_spill + Q_sluice)
    + (1 - do_pass) * (1 - do_poolq) * do_set_q_out * Q_out_from_input
  );

  // This equation creates a 'bookkeeping' variable that closes the mass-balance when compute_v = 0
  Q_out_corrected = Q_out -  Q_error;

end Reservoir;
