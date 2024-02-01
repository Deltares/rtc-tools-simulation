model SingleReservoir
  Deltares.ChannelFlow.SimpleRouting.Storage.Storage reservoir(Q_release = Q_out, V(start=reservoir_init_volume, fixed=true, nominal = 100));
  Deltares.ChannelFlow.SimpleRouting.BoundaryConditions.Inflow inflow(Q = Q_in);
  Deltares.ChannelFlow.SimpleRouting.BoundaryConditions.Terminal outflow;

  parameter Modelica.SIunits.Volume reservoir_init_volume;
  input Modelica.SIunits.VolumeFlowRate Q_out(fixed = true);
  input Modelica.SIunits.VolumeFlowRate Q_in(fixed = true);
  output Modelica.SIunits.Volume reservoir_V = reservoir.V;
  output Modelica.SIunits.VolumeFlowRate Q_release = Q_out;
equation
  connect(inflow.QOut, reservoir.QIn);
  connect(reservoir.QOut, outflow.QIn);
end SingleReservoir;
