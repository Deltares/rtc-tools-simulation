model ExampleThreeBoxesTwoBndZSF
  import SI = Modelica.Units.SI;
  replaceable package Medium = Deltares.ChannelFlow.Media.SalineWater;
  // Inputs
  //Upstream and downstream discharge and flux
  //input Modelica.Units.SI.VolumeFlowRate upstream_discharge(fixed = true);
  //input Modelica.Units.SI.VolumeFlowRate downstream_discharge(fixed = true);
  //input Modelica.Units.SI.MassFlowRate upstream_flux;
  
  
  //Lateral discharge and flux to every active storage
  input SI.VolumeFlowRate storage1_qforcing_in;
  input SI.VolumeFlowRate storage2_qforcing_in;
  input SI.VolumeFlowRate storage3_qforcing_in;
  
  input SI.VolumeFlowRate storage1_qforcing_out;
  input SI.VolumeFlowRate storage2_qforcing_out;
  input SI.VolumeFlowRate storage3_qforcing_out;
  
  input SI.MassFlowRate storage1_mforcing_in;
  input SI.MassFlowRate storage2_mforcing_in;
  input SI.MassFlowRate storage3_mforcing_in;

//ZSF discharges and fluxes to upstream and downstream storage
  input SI.VolumeFlowRate storage3_qforcing_ZSF;
  input SI.VolumeFlowRate storage3_mforcing_ZSF;
  input SI.VolumeFlowRate storage1_qforcing_ZSF;
  input SI.VolumeFlowRate storage1_mforcing_ZSF;

//Advective forcing upstream and downstream - now only downstream is used
  input SI.VolumeFlowRate storage1_qforcing_advective;
  input SI.MassFlowRate storage1_mforcing_advective;
  input SI.VolumeFlowRate storage3_qforcing_advective;

//Advective discharge between the storages
  input SI.VolumeFlowRate connector_0_middle_discharge;
  input SI.VolumeFlowRate connector_1_middle_discharge;
  input SI.VolumeFlowRate connector_2_middle_discharge;
  input SI.VolumeFlowRate connector_3_middle_discharge;

// Output concentration
  output SI.Density concentration_storage1(fixed = false) = storage1.HQUp.C[1];
  output SI.Density concentration_storage2 = storage2.HQUp.C[1];
  output SI.Density concentration_storage0 = storage0.HQUp.C[1];
  output SI.Density concentration_storage3 = storage3.HQUp.C[1];
  output SI.Density concentration_storage4 = storage4.HQUp.C[1];
 //Output flux
  output SI.MassFlowRate connector_0_M_Up(start = 1.0)=connector_0.HQUp.M[1];
  output SI.MassFlowRate connector_1_M_Up(start = 1.0)=connector_1.HQUp.M[1];
  output SI.MassFlowRate connector_2_M_Up(start = 1.0)=connector_2.HQUp.M[1];
  output SI.MassFlowRate connector_3_M_Up(start = 1.0)=connector_3.HQUp.M[1];

  Deltares.ChannelFlow.Salt.Elements.SubstanceControlledStructure connector_0(redeclare package medium = Medium, temperature_up = 16.0, temperature_down = 16.0, width = 2000.0, H_b_up = 0.0, H_b_down = 0.0) annotation(
    Placement(visible = true, transformation(origin = {-90, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SubstanceControlledStructure connector_1(redeclare package medium = Medium, temperature_up = 16.0, temperature_down = 16.0, width = 2000.0, H_b_up = 0.0, H_b_down = 0.0) annotation(
    Placement(visible = true, transformation(origin = {-30, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SubstanceControlledStructure connector_2(redeclare package medium = Medium, temperature_up = 16.0, temperature_down = 16.0, width = 2000.0, H_b_up = 0.0, H_b_down = 0.0) annotation(
    Placement(visible = true, transformation(origin = {25, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SubstanceControlledStructure connector_3(redeclare package medium = Medium, temperature_up = 16.0, temperature_down = 16.0, width = 2000.0, H_b_up = 0.0, H_b_down = 0.0) annotation(
    Placement(visible = true, transformation(origin = {100, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SaltyLinearReservoirBnd storage0(redeclare package medium = Medium, H_b = 0.0, A=400000000.0, Q_turbine = 0.0, Q_spill = 0.0, V_nominal = 1.0) annotation(
    Placement(visible = true, transformation(origin = {-120, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SaltyLinearReservoir storage1(redeclare package medium = Medium, H_b = 0.0, A=400000000.0, Q_turbine = 0.0, Q_spill = 0.0, V_nominal = 1.0, n_QForcing=4) annotation(
    Placement(visible = true, transformation(origin = {-55, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SaltyLinearReservoir storage2(redeclare package medium = Medium, H_b = 0.0, A=400000.0, Q_turbine = 0.0, Q_spill = 0.0, V_nominal = 1.0, n_QForcing=2) annotation(
    Placement(visible = true, transformation(origin = {-5, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SaltyLinearReservoir storage3(redeclare package medium = Medium, H_b = 0.0, A=400000.0, Q_turbine = 0.0, Q_spill = 0.0, V_nominal = 1.0, n_QForcing=4) annotation(
    Placement(visible = true, transformation(origin = {65, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SaltyLinearReservoirBnd storage4(redeclare package medium = Medium, H_b = 0.0, A=400000000.0, Q_turbine = 0.0, Q_spill = 0.0, V_nominal = 1.0) annotation(
    Placement(visible = true, transformation(origin = {135, 5}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));

equation
  connect(storage1.HQUp, connector_0.HQDown) annotation(
    Line(points = {{-63, 5}, {-82, 5}}, color = {0, 0, 255}));
  connect(storage1.HQDown, connector_1.HQUp) annotation(
    Line(points = {{-47, 5}, {-38, 5}}, color = {0, 0, 255}));
  connect(storage2.HQUp, connector_1.HQDown) annotation(
    Line(points = {{-13, 5}, {-22, 5}}, color = {0, 0, 255}));
  connect(storage2.HQDown, connector_2.HQUp) annotation(
    Line(points = {{3, 5}, {17, 5}}, color = {0, 0, 255}));
  connect(storage3.HQUp, connector_2.HQDown) annotation(
    Line(points = {{57, 5}, {33, 5}}, color = {0, 0, 255}));
   connect(storage3.HQDown, connector_3.HQUp) annotation(
    Line(points = {{73, 5}, {92, 5}}, color = {0, 0, 255}));
 connect(connector_3.HQDown, storage4.HQUp) annotation(
    Line(points = {{110, 5}, {125, 5}}, color = {0, 0, 255}));
 connect(storage0.HQDown, connector_0.HQUp) annotation(
    Line(points = {{-110, 5}, {-100, 5}}, color = {0, 0, 255}));
  annotation(
    Diagram(coordinateSystem(extent = {{-148.5, -105}, {148.5, 105}}, initialScale = 0.1, grid = {5, 5})));
end ExampleThreeBoxesTwoBndZSF;
