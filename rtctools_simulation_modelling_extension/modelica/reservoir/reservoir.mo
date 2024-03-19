model Reservoir
  import SI = Modelica.SIunits;

  parameter SI.Length H_crest();

  input SI.VolumeFlowRate Q_in();
  input SI.VolumeFlowRate Q_turbine();
  input Boolean do_spill;
  input Boolean do_pass;

  output SI.Volume V();
  output SI.VolumeFlowRate Q_out();
  output SI.Length H();
  SI.Area Area();
  SI.VolumeFlowRate Q_spill_from_lookup_table();
  output SI.VolumeFlowRate Q_spill();

equation
  // Lookup tables:
  // V -> Area
  // V -> H
  // H -> QSpill_from_lookup_table

  der(V) = Q_in - Q_out;
  Q_spill = do_spill * Q_spill_from_lookup_table;
  Q_out = do_pass * Q_in + (1 - do_pass) * (Q_turbine + Q_spill);
    
end Reservoir;
