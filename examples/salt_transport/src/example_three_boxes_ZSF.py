import copy
import logging

import numpy as np
import pandas as pd
import pyzsf
from rtctools.simulation.csv_mixin import CSVMixin
from rtctools.simulation.simulation_problem import SimulationProblem
from rtctools.util import run_simulation_problem
from rtctools_interface.simulation.plot_mixin import PlotMixin

from rtctools_simulation.salt_simulation_mixin import SaltSimulationMixin

logger = logging.getLogger("rtctools")


def zsf_routines(
    self, routine, t_level, t_open_lake, t_flushing, t_open_sea, salinity_lake, parameters
):
    level_to_fresh_side = 1
    door_open_on_fresh_side = 2
    leveling_to_salt_side = 3
    door_open_on_salt_side = 4
    flushing_2 = -2
    flushing_4 = -4
    if routine == level_to_fresh_side:
        assert t_level > 0
        print(self.z.state)
        results = self.z.step_phase_1(t_level, **parameters)
        print(parameters)
        print("Phase 1")
        print(self.z.state)
        print(results)
        pass
    elif routine == door_open_on_fresh_side:
        results = self.z.step_phase_2(t_open_lake, **parameters)
    elif routine == leveling_to_salt_side:
        assert t_level > 0
        print(self.z.state)
        results = self.z.step_phase_3(t_level, **parameters)
        print(self.z.state)
    elif routine == door_open_on_salt_side:
        print(self.z.state)
        results = self.z.step_phase_4(t_open_sea, **parameters)
        print(self.z.state)
    elif routine in {flushing_2, flushing_4}:
        results = self.z.step_flush_doors_closed(t_flushing, **parameters)
    else:
        raise Exception(f"Unknown routine '{routine}'")
    print("Salinity lock: {}".format(self.z.state["salinity_lock"]))
    self.netto_q_in, self.netto_flux = from_zsf_results_to_netto_flux(results, salinity_lake)

    return results


def use_zsf_usptream_phase_wise(self, time_step):
    # netto_q_in = 0.0
    # netto_flux = 0.0
    if (
        int(self.get_current_time()) == int(self.start_lockage_time)
        and self.locking_index < self.number_of_operations
    ):
        print("Now we lock: {}".format(self.start_lockage_time))
        print("Salinity lock before operation: {}".format(self.z.state["salinity_lock"]))

        parameters = self.lockages[self.locking_index]

        t_open_lake = parameters.pop("t_open_lake")
        t_open_sea = parameters.pop("t_open_sea")
        t_level = parameters.pop("t_level")
        t_flushing = parameters.pop("t_flushing")
        duration = np.nansum([t_open_lake, t_open_sea, t_level, t_flushing])

        # duration = self.df_time[self.locking_index]
        self.end_lockage_time = self.start_lockage_time + duration
        # To ZSF

        salinity_lake = self.get_var(self.active_storage_names[0] + ".C")
        head_sea_upstream_zsf = self.io.get_timeseries("head_sea_upstream_zsf")[1][int(time_step)]
        salinity_sea_upstream_zsf = self.io.get_timeseries("salinity_sea_upstream_zsf")[1][
            int(time_step)
        ]

        print("Salinity sea: {}".format(salinity_sea_upstream_zsf))
        print("Salinity lake: {}".format(salinity_lake))

        parameters = self.lockages[self.locking_index]

        parameters["salinity_lake"] = salinity_lake
        parameters["head_sea"] = head_sea_upstream_zsf
        parameters["salinity_sea"] = salinity_sea_upstream_zsf
        parameters["head_lake"] = 10.0

        routine = int(parameters.pop("routine"))
        """
        t_open_lake = parameters.pop("t_open_lake")
        t_open_sea = parameters.pop("t_open_sea")
        t_level = parameters.pop("t_level")
        t_flushing = parameters.pop("t_flushing")
        """

        results = zsf_routines(
            self, routine, t_level, t_open_lake, t_flushing, t_open_sea, salinity_lake, parameters
        )

        logger.debug("ZSF results: {}".format(results))

        self.locking_index += 1
        # Here we calculate the next lockage time
        if self.locking_index < self.number_of_operations:
            self.start_lockage_time = self.df_time[self.locking_index]
        else:
            self.start_lockage_time = 0

    if self.end_lockage_time > self.get_current_time():
        pass
    else:
        self.netto_q_in = 0.0
        self.netto_flux = 0.0

    print("Netto Q = {:.1f} m3/s".format(self.netto_q_in))
    print("Netto Flux = {:.1f} kg/s".format(self.netto_flux))
    self.set_var(self.active_storage_names[0] + "_qforcing_ZSF", self.netto_q_in)
    self.set_var(self.active_storage_names[0] + "_mforcing_ZSF", self.netto_flux)
    netto_q_in = self.netto_q_in

    return netto_q_in


def use_zsf_upstream(self, time_step):
    if self.use_zsf_upstream_phase_wise:
        netto_q_in = use_zsf_usptream_phase_wise(self, time_step)

    else:
        # To ZSF
        head_lake = self.get_var(self.active_storage_names[0] + ".H")
        salinity_lake = self.get_var(self.active_storage_names[0] + ".C")
        head_sea_upstream_zsf = self.io.get_timeseries("head_sea_upstream_zsf")[1][int(time_step)]
        salinity_sea_upstream_zsf = self.io.get_timeseries("salinity_sea_upstream_zsf")[1][
            int(time_step)
        ]

        lock_parameters = {
            "lock_length": 280.0,
            "lock_width": 48.0,
            "lock_bottom": 3.75,
        }
        boundary_conditions = {
            "head_lake": head_lake,
            "salinity_lake": salinity_lake,
            "temperature_lake": 15.0,
            "head_sea": head_sea_upstream_zsf,
            "salinity_sea": salinity_sea_upstream_zsf,
            "temperature_sea": 15.0,
        }
        mitigation_parameters = {"density_current_factor_lake": 1.0}
        operational_parameters = {
            "num_cycles": 13,
            "door_time_to_open": 300.0,
            "leveling_time": 300.0,
            "ship_volume_sea_to_lake": 1000.0,
            "ship_volume_lake_to_sea": 1000.0,
        }

        netto_q_in, netto_flux = call_zsf(
            head_lake,
            salinity_lake,
            lock_parameters,
            boundary_conditions,
            mitigation_parameters,
            operational_parameters,
        )

        print("Netto Q = {:.1f} kg/s".format(netto_q_in))
        print("Netto Flux = {:.1f} kg/s".format(netto_flux))
        self.set_var(self.active_storage_names[0] + "_qforcing_ZSF", netto_q_in)
        self.set_var(self.active_storage_names[0] + "_mforcing_ZSF", netto_flux)

    return netto_q_in


def use_zsf_downstream(self, time_step):
    # Data to ZSF
    head_lake = self.get_var(self.active_storage_names[-1] + ".H")
    salinity_lake = self.get_var(self.active_storage_names[-1] + ".C")
    head_sea_downstream_zsf = self.io.get_timeseries("head_sea_downstream_zsf")[1][int(time_step)]
    salinity_sea_downstream_zsf = self.io.get_timeseries("salinity_sea_downstream_zsf")[1][
        int(time_step)
    ]

    # Parameters to ZSF
    lock_parameters = {
        "lock_length": 148.0,
        "lock_width": 14.0,
        "lock_bottom": -4.4,
    }
    boundary_conditions = {
        "head_lake": head_lake,
        "salinity_lake": salinity_lake,
        "temperature_lake": 15.0,
        "head_sea": head_sea_downstream_zsf,
        "salinity_sea": salinity_sea_downstream_zsf,
        "temperature_sea": 15.0,
    }
    operational_parameters = {
        "num_cycles": 30,
        "door_time_to_open": 300.0,
        "leveling_time": 300.0,
        "ship_volume_sea_to_lake": 1000.0,
        "ship_volume_lake_to_sea": 1000.0,
    }

    mitigation_parameters = {"density_current_factor_lake": 1.0}

    netto_q_in_down, netto_flux = call_zsf(
        head_lake,
        salinity_lake,
        lock_parameters,
        boundary_conditions,
        mitigation_parameters,
        operational_parameters,
    )

    self.set_var(self.active_storage_names[-1] + "_qforcing_ZSF", -netto_q_in_down)
    self.set_var(self.active_storage_names[0] + "_mforcing_ZSF", -netto_flux)

    print("Netto Q downstream = {:.1f} kg/s".format(-netto_q_in_down))
    print("Netto Flux downstream = {:.1f} kg/s".format(-netto_flux))

    return netto_q_in_down


def from_zsf_results_to_netto_flux(results, salinity_lake):
    discharge_from_lake = results["discharge_from_lake"]
    discharge_to_lake = results["discharge_to_lake"]
    salinity_to_lake = results["salinity_to_lake"]

    # Calcualte netto flux
    netto_q_in = discharge_to_lake - discharge_from_lake
    netto_flux = (discharge_to_lake * salinity_to_lake) - (discharge_from_lake * salinity_lake)

    return netto_q_in, netto_flux


def call_zsf(
    head_lake,
    salinity_lake,
    lock_parameters,
    boundary_conditions,
    mitigation_parameters,
    operational_parameters,
):
    daytime_parameters = {
        **lock_parameters,
        **boundary_conditions,
        **mitigation_parameters,
        **operational_parameters,
    }
    # nighttime_parameters = {**daytime_parameters, "num_cycles": 10}
    results = pyzsf.zsf_calc_steady(**daytime_parameters)

    discharge_from_lake = results["discharge_from_lake"]
    discharge_to_lake = results["discharge_to_lake"]
    salinity_to_lake = results["salinity_to_lake"]

    # Calcualte netto flux
    netto_q_in = discharge_to_lake - discharge_from_lake
    netto_flux = (discharge_to_lake * salinity_to_lake) - (discharge_from_lake * salinity_lake)

    return netto_q_in, netto_flux


class ExampleThreeBoxesZSF(PlotMixin, SaltSimulationMixin, CSVMixin, SimulationProblem):
    # Basic settings
    upstream_open_boundary = False
    downstream_open_boundary = False
    use_zsf_upstream = True
    use_zsf_downstream = False
    water_level_closing = False
    discharge_closing = False
    use_zsf_upstream_phase_wise = True
    use_zsf_downstream_phase_wise = False

    if upstream_open_boundary and downstream_open_boundary:
        model_name = "ExampleThreeBoxesTwoBndZSF"
    elif upstream_open_boundary:
        model_name = "ExampleThreeBoxesUpBndZSF"
    elif downstream_open_boundary:
        model_name = "ExampleThreeBoxesDownBndZSF"
    else:
        model_name = "ExampleThreeBoxesZSF"

    active_storage_names = ["storage1", "storage2", "storage3"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TMP: for pictures
        self.__output_folder = kwargs["output_folder"]

    def initialize(self):
        # The model needs to know the storages where calculations occur
        self.storage_names = copy.deepcopy(self.active_storage_names)
        self.connector_names = ["connector_1", "connector_2"]

        if self.upstream_open_boundary:
            upstream_boundary_name = "storage0"
            self.storage_names.insert(0, upstream_boundary_name)
            self.connector_names.insert(0, "connector_0")

        if self.downstream_open_boundary:
            upstream_boundary_name = "storage4"
            self.storage_names.append(upstream_boundary_name)
            self.connector_names.append("connector_3")

        super().initialize()

    def pre(self) -> None:
        super().pre()

        if self.use_zsf_upstream_phase_wise or self.use_zsf_downstream_phase_wise:
            df_lockages = pd.read_csv(self._input_folder + r"\lockages.csv", index_col=0)
            self.df_time = df_lockages.index
            self.lockages = list(df_lockages.to_dict("records"))
            self.start_lockage_time = self.df_time[0]
            self.locking_index = 0
            self.end_lockage_time = 0
            self.number_of_operations = len(self.df_time)

            lock_parameters = {
                "lock_length": 30.0,
                "lock_width": 1000.0,
                "lock_bottom": 0.0,
            }
            head_lake = self.get_var(self.active_storage_names[0] + ".H")
            constant_boundary_conditions = {
                "head_lake": head_lake,
                "temperature_lake": 15.0,
                "temperature_sea": 15.0,
            }

            mitigation_parameters = {
                "density_current_factor_lake": 0.25,
                "density_current_factor_sea": 0.25,
                "distance_door_bubble_screen_lake": 10.0,
                "distance_door_bubble_screen_sea": 10.0,
                "flushing_discharge_high_tide": 0.0,
                "flushing_discharge_low_tide": 0.0,
                "sill_height_lake": 0.5,
            }

            # Initialize the lock
            self.z = pyzsf.ZSFUnsteady(
                15.0,
                11.0,
                **lock_parameters,
                **constant_boundary_conditions,
                **mitigation_parameters,
            )
            print("Salinity lock after initialization: {}".format(self.z.state["salinity_lock"]))

    def update(self, dt):
        time_step = self.get_current_time() / self.get_time_step()
        print(time_step)

        if self.use_zsf_upstream:
            netto_q_in = use_zsf_upstream(self, time_step)

        if self.use_zsf_downstream:
            netto_q_in_down = use_zsf_downstream(self, time_step)

        self.ZSF_Q = [0, 0]
        if self.use_zsf_upstream and self.use_zsf_upstream_phase_wise:
            self.ZSF_Q[0] = self.netto_q_in
        elif self.use_zsf_upstream:
            self.ZSF_Q[0] = netto_q_in
        if self.use_zsf_downstream:
            self.ZSF_Q[1] = netto_q_in_down

        super().update(dt)

    def post(self):
        super().post()


# Run
run_simulation_problem(ExampleThreeBoxesZSF, log_level=logging.DEBUG)
