model Reservoir
  type FlowRatePerArea = Real(unit = "mm/hour");
  import SI = Modelica.SIunits;

  // Parameters
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
  input Boolean include_evaporation(fixed=true);
  input Boolean include_rain(fixed=true);
  input FlowRatePerArea mm_evaporation_per_hour(fixed=true);
  input FlowRatePerArea mm_rain_per_hour(fixed=true);
  input Integer day(fixed=true);

  // Outputs/Intermediates
  output SI.Volume V();
  SI.Volume V_observed();
  output SI.VolumeFlowRate Q_out();
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

  der(V) - (Q_in - Q_out + Q_rain - Q_evap) = 0;

  Q_evap = Area * mm_evaporation_per_hour / 3600 / 1000 * include_evaporation;
  Q_rain = max_reservoir_area * mm_rain_per_hour / 3600 / 1000 * include_rain;

  Q_spill = do_spill * Q_spill_from_lookup_table;

  Q_out = (
    do_pass * Q_in
    + do_poolq * Q_out_from_lookup_table
    + use_composite_q * (Q_turbine + Q_spill + Q_sluice)
    + do_set_q_out * Q_out_from_input
  );

end Reservoir;
