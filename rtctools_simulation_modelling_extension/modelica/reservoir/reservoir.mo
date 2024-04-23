model Reservoir
  type FlowRatePerArea = Real(unit = "mm/hour");
  import SI = Modelica.SIunits;

  parameter SI.Length H_crest();

  input SI.VolumeFlowRate Q_in();
  input SI.VolumeFlowRate Q_turbine();
  input Boolean do_spill;
  input Boolean do_pass;
  input Boolean do_poolq;
  input Boolean include_evaporation;
  input Boolean include_rain;
  input FlowRatePerArea mm_evaporation_per_hour();
  input FlowRatePerArea mm_rain_per_hour();
  parameter SI.Area max_reservoir_area() = 0;

  output SI.Volume V();
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

  Q_evap = Area * mm_evaporation_per_hour / 3600 / 1000 * include_evaporation;
  Q_rain = max_reservoir_area * mm_rain_per_hour / 3600 / 1000 * include_rain;

  der(V) = Q_in - Q_out + Q_rain - Q_evap;
  Q_spill = do_spill * Q_spill_from_lookup_table;
  Q_out = (
    do_pass * Q_in
    + do_poolq * Q_out_from_lookup_table
    + (1 - do_pass) * (1 - do_poolq) * (Q_turbine + Q_spill)
  );
    
end Reservoir;
