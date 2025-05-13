model ReservoirMinQ
  import SI = Modelica.SIunits;
  input SI.VolumeFlowRate Q_in(fixed=true);
  input SI.VolumeFlowRate Q_out(fixed=false);
  output SI.Volume V();
  output SI.VolumeFlowRate Q_out_max();

equation
  der(V) = Q_in - Q_out;
  der(Q_out_max) = 0;

end ReservoirMinQ;
