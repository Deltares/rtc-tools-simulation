model ExampleThreeBoxesZSF
  replaceable package Medium = Deltares.ChannelFlow.Media.SalineWater;
  // Inputs
  import SI = Modelica.Units.SI;
  //Upstream and downstream discharge and flux
  input SI.VolumeFlowRate upstream_discharge(fixed = true);
  input SI.VolumeFlowRate downstream_discharge(fixed = true);
  input SI.MassFlowRate upstream_flux;
  
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
  input SI.MassFlowRate storage3_mforcing_ZSF;
  input SI.VolumeFlowRate storage1_qforcing_ZSF;
  input SI.MassFlowRate storage1_mforcing_ZSF;

//Advective forcing upstream and downstream - now only downstream is used
  input SI.VolumeFlowRate storage1_qforcing_advective;
  input SI.MassFlowRate storage1_mforcing_advective;
  input SI.VolumeFlowRate storage3_qforcing_advective;

//Advective discharge between the storages
  input SI.VolumeFlowRate connector_1_middle_discharge;
  input SI.VolumeFlowRate connector_2_middle_discharge;

// Output concentration
  output Modelica.Units.SI.Density concentration_storage1 = storage1.HQUp.C[1];
  output Modelica.Units.SI.Density concentration_storage2 = storage2.HQUp.C[1];
  output Modelica.Units.SI.Density concentration_storage3 = storage3.HQUp.C[1];
 //Output flux
  output SI.MassFlowRate connector_1_M_Up(start = 1.0)=connector_1.HQUp.M[1];
  output SI.MassFlowRate connector_2_M_Up(start = 1.0)=connector_2.HQUp.M[1];
  
  output SI.Height storage2_H = storage2.HQUp.H;
  output SI.Height storage3_H = storage3.HQUp.H;

  
  Deltares.ChannelFlow.Hydraulic.BoundaryConditions.Discharge Terminal(redeclare package medium = Medium, upwind = false) annotation(
    Placement(visible = true, transformation(origin = {125, 10}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Deltares.ChannelFlow.Salt.Elements.SubstanceControlledStructure connector_1(redeclare package medium = Medium, temperature_up = 16.0, temperature_down = 16.0, width = 2000.0, H_b_up = -5.0, H_b_down = -5.0) annotation(
    Placement(visible = true, transformation(origin = {-50, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SubstanceControlledStructure connector_2(redeclare package medium = Medium, temperature_up = 16.0, temperature_down = 16.0, width = 2000.0, H_b_up = -5.0, H_b_down = -5.0) annotation(
    Placement(visible = true, transformation(origin = {35, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Hydraulic.BoundaryConditions.Discharge Inflow(redeclare package medium = Medium, upwind = false) annotation(
    Placement(visible = true, transformation(origin = {-135, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Deltares.ChannelFlow.Salt.Elements.SaltyLinearReservoir storage1(redeclare package medium = Medium, H_b = -5.0, A=400000.0, Q_turbine = 0.0, Q_spill = 0.0, V_nominal = 1.0, n_QForcing=4) annotation(
    Placement(visible = true, transformation(origin = {-95, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SaltyLinearReservoir storage2(redeclare package medium = Medium, H_b = -5.0, A=400000.0, Q_turbine = 0.0, Q_spill = 0.0, V_nominal = 1.0, n_QForcing=2) annotation(
    Placement(visible = true, transformation(origin = {-5, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.Salt.Elements.SaltyLinearReservoir storage3(redeclare package medium = Medium, H_b = -5.0, A=400000.0, Q_turbine = 0.0, Q_spill = 0.0, V_nominal = 1.0, n_QForcing=4) annotation(
    Placement(visible = true, transformation(origin = {80, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));

	
equation


  connect(storage1.HQUp, Inflow.HQ) annotation(
    Line(points = {{10, 5}, {-45, 5}, {-45, 0}, {-45, 0}}, color = {0, 0, 255}));
  connect(storage1.HQDown, connector_1.HQUp) annotation(
    Line(points = {{10, 5}, {-45, 5}, {-45, 0}, {-45, 0}}, color = {0, 0, 255}));
  connect(storage2.HQUp, connector_1.HQDown) annotation(
    Line(points = {{10, 5}, {-45, 5}, {-45, 0}, {-45, 0}}, color = {0, 0, 255}));
  connect(storage2.HQDown, connector_2.HQUp) annotation(
    Line(points = {{0, -5}, {45, -5}, {45, -10}, {45, -10}}, color = {0, 0, 255}));
  connect(storage3.HQUp, connector_2.HQDown) annotation(
    Line(points = {{0, -5}, {45, -5}, {45, -10}, {45, -10}}, color = {0, 0, 255}));
   connect(storage3.HQDown, Terminal.HQ) annotation(
    Line(points = {{0, -5}, {45, -5}, {45, -10}, {45, -10}}, color = {0, 0, 255}));


  
  Terminal.M = downstream_discharge * storage3.HQDown.C;
  Inflow.M[1] = upstream_flux;
  Terminal.Q = downstream_discharge;
  Inflow.Q = upstream_discharge;


  annotation(
    Diagram(coordinateSystem(extent = {{-148.5, -105}, {148.5, 105}}, initialScale = 0.1, grid = {5, 5})));
end ExampleThreeBoxesZSF;
