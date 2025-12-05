import logging

# from symbol import parameters
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger("rtctools")


def area_coef(storage_areas, number):
    coef = 0.0
    for idx in range(len(storage_areas)):
        coef += storage_areas[number] / storage_areas[idx]
    return coef


def set_mid_q_wl_closing(self, net_q_storages, net_q_system):
    storage_areas = [self.parameters()[x + ".A"] for x in self.active_storage_names]
    minimum_allowed_negative_q = -0.001
    for idx, storage_name in enumerate(self.active_storage_names):
        if idx == 0:
            q_net_previous = 0
        if idx == len(self.active_storage_names) - 1:
            pass
        else:
            q_net_box_needed = net_q_system / area_coef(storage_areas, idx)

            q_mid_set = q_net_previous + net_q_storages[idx] - q_net_box_needed
            q_net_previous = q_mid_set
            if q_mid_set < minimum_allowed_negative_q:
                logger.debug(
                    "{} has negative downstream discharge, check the laterals.".format(storage_name)
                )
                # raise Exception
            if self.upstream_open_boundary:
                connector_name = self.connector_names[idx + 1]
            else:
                connector_name = self.connector_names[idx]
            self.set_var(connector_name + "_middle_discharge", q_mid_set)
            logger.debug(
                "Q mid set for {} at {}: {}".format(
                    storage_name, self.get_current_time(), q_mid_set
                )
            )


def set_mid_q_q_closing(self, net_q_storages, net_q_system):
    minimum_allowed_negative_q = -0.001
    for idx, storage_name in enumerate(self.active_storage_names):
        if idx == 0:
            q_net_previous = 0
        if idx == len(self.active_storage_names) - 1:
            q_mid_set = q_net_previous + net_q_storages[idx]
            self.set_var(storage_name + "_qforcing_advective", -q_mid_set)
            logger.debug(
                "Q down set for {} at {}: {}".format(
                    storage_name, self.get_current_time(), q_mid_set
                )
            )
        else:
            q_mid_set = q_net_previous + net_q_storages[idx]
            q_net_previous = q_mid_set
            if q_mid_set < minimum_allowed_negative_q:
                logger.debug(
                    "{} has negative downstream discharge, check the laterals.".format(storage_name)
                )
                raise Exception
            if self.upstream_open_boundary:
                connector_name = self.connector_names[idx + 1]
            else:
                connector_name = self.connector_names[idx]
            self.set_var(connector_name + "_middle_discharge", q_mid_set)
            logger.debug(
                "Q mid set for {} at {}: {}".format(
                    storage_name, self.get_current_time(), q_mid_set
                )
            )


def add_equations_middle_q_m(self):
    variables = self.get_variables()

    for name in self.connector_names:
        var_in = name + ".HQUp.M[1]"
        var_out = name + ".HQDown.M[1]"
        var_in_mx = variables[var_in]
        var_out_mx = variables[var_out]
        self.equation_list.append(var_in_mx + var_out_mx)

        var_in = name + ".HQDown.Q"
        var_out = name + "_middle_discharge"
        var_in_mx = variables[var_in]
        var_out_mx = variables[var_out]
        self.equation_list.append(var_in_mx + var_out_mx)

        var_in = name + ".HQUp.Q"
        var_out = name + "_middle_discharge"
        var_in_mx = variables[var_in]
        var_out_mx = variables[var_out]
        self.equation_list.append(var_in_mx - var_out_mx)


def add_equations_forcings(self):
    variables = self.get_variables()

    for idx, name in enumerate(self.active_storage_names):
        var_in = name + ".QForcing[1]"
        var_out = name + "_qforcing_in"
        var_in_mx = variables[var_in]
        var_out_mx = variables[var_out]
        self.equation_list.append(var_in_mx - var_out_mx)

        var_in = name + ".QForcing[2]"
        var_out = name + "_qforcing_out"
        var_in_mx = variables[var_in]
        var_out_mx = variables[var_out]
        self.equation_list.append(var_in_mx - var_out_mx)

        var_in = name + ".MForcing[1]"
        var_out = name + "_mforcing_in"
        var_in_mx = variables[var_in]
        var_out_mx = variables[var_out]
        self.equation_list.append(var_in_mx - var_out_mx)

        var_in = name + ".MForcing[2]"
        var_out = name + "_qforcing_out"
        var_out_mul = name + ".HQDown.C[1]"
        var_in_mx = variables[var_in]
        var_out_mx = variables[var_out]
        var_out_mul_mx = variables[var_out_mul]
        self.equation_list.append(var_in_mx - var_out_mx * var_out_mul_mx)

        if idx == 0:
            var_in = name + ".QForcing[4]"
            var_out = name + "_qforcing_advective"
            var_in_mx = variables[var_in]
            var_out_mx = variables[var_out]
            self.equation_list.append(var_in_mx - var_out_mx)

            var_in = name + ".MForcing[4]"
            var_out = name + "_mforcing_advective"
            var_in_mx = variables[var_in]
            var_out_mx = variables[var_out]
            self.equation_list.append(var_in_mx - var_out_mx)

        if idx == len(self.active_storage_names) - 1:
            var_in = name + ".QForcing[4]"
            var_out = name + "_qforcing_advective"
            var_in_mx = variables[var_in]
            var_out_mx = variables[var_out]
            self.equation_list.append(var_in_mx - var_out_mx)

            var_in = name + ".MForcing[4]"
            var_out = name + "_qforcing_advective"
            var_out_mul = name + ".HQDown.C[1]"
            var_in_mx = variables[var_in]
            var_out_mx = variables[var_out]
            var_out_mul_mx = variables[var_out_mul]
            self.equation_list.append(var_in_mx - var_out_mx * var_out_mul_mx)


def add_equations_zsf(self):
    variables = self.get_variables()

    for idx, name in enumerate(self.active_storage_names):
        if idx in (0, len(self.active_storage_names) - 1):
            # ZSF

            var_in = name + ".QForcing[3]"
            var_out = name + "_qforcing_ZSF"
            var_in_mx = variables[var_in]
            var_out_mx = variables[var_out]
            self.equation_list.append(var_in_mx - var_out_mx)
            logger.debug("Appending equation: in: {} and out: {}".format(var_in, var_out))

            var_in = name + ".MForcing[3]"
            var_out = name + "_mforcing_ZSF"
            var_in_mx = variables[var_in]
            var_out_mx = variables[var_out]
            self.equation_list.append(var_in_mx - var_out_mx)
            logger.debug("Appending equation: in: {} and out: {}".format(var_in, var_out))


def axis_settings(axis, title, ylabel=None, empty_plot=False):
    ymin, ymax = axis.get_ylim()
    axis.set_ylim(ymin - 0.1, ymax + 0.1)
    if not empty_plot:
        axis.legend()
    axis.set_title(title, fontsize=10)
    if ylabel is not None:
        axis.set_ylabel(ylabel)

    return axis


def create_plot1(self, axarr, results, color_list):
    times = self.times() / 3600
    # Plot 1
    if self.upstream_open_boundary:
        axarr[0].plot(
            times,
            results["concentration_" + self.storage_names[0]],
            label=self.storage_names[0] + "C",
            linewidth=2,
            color="blue",
        )

    for idx, storage_name in enumerate(self.active_storage_names):
        axarr[0].plot(
            times,
            results["concentration_" + storage_name],
            label=storage_name + "C",
            linewidth=2,
            color=color_list[idx],
        )

    if self.downstream_open_boundary:
        axarr[0].plot(
            times,
            results["concentration_" + self.storage_names[-1]],
            label=self.storage_names[-1] + "C",
            linewidth=2,
            color="red",
        )

    axis_settings(axarr[0], "Concentrations")


def create_plot2(self, axarr, results, color_list):
    times = self.times() / 3600

    # Plot 2
    for idx, storage_name in enumerate(self.active_storage_names):
        axarr[1].plot(
            times,
            results[storage_name + ".V"] / self.parameters()[storage_name + ".A"]
            + self.parameters()[storage_name + ".H_b"],
            linewidth=2,
            color=color_list[idx],
            linestyle="-",
            label="H_" + storage_name,
        )
    if self.upstream_open_boundary:
        axarr[1].plot(
            times,
            results[self.storage_names[0] + ".V"]
            / (self.parameters()[self.storage_names[0] + ".A"])
            + self.parameters()[self.storage_names[0] + ".H_b"],
            label="meer",
            linewidth=2,
            color="b",
        )
    if self.downstream_open_boundary:
        axarr[1].plot(
            times,
            results[self.storage_names[-1] + ".V"]
            / (self.parameters()[self.storage_names[-1] + ".A"])
            + self.parameters()[self.storage_names[-1] + ".H_b"],
            label="zee",
            linewidth=2,
            color="r",
            linestyle="--",
        )

    axis_settings(axarr[1], "Water levels", ylabel="Water level\n[m]")


def create_plot3(self, axarr, results, color_list):
    times = self.times() / 3600

    # Plot 3
    for idx, connector_name in enumerate(self.connector_names):
        if self.upstream_open_boundary and idx == 0:
            axarr[2].plot(
                times,
                results[connector_name + ".flux_q1_s1"],
                label="q_uit_" + connector_name,
                linewidth=2,
                color="b",
            )
        # elif self.downstream_open_boundary and idx==len(self.connector_names)-1:
        #    axarr[2].plot(times, results[connector_name + '.flux_q1_s1'],
        #                  label='q_uit_' + connector_name, linewidth=2, color=color_list[idx])
        else:
            axarr[2].plot(
                times,
                results[connector_name + ".flux_q1_s1"],
                label="q_uit_" + connector_name,
                linewidth=2,
                color=color_list[idx],
            )
    axis_settings(axarr[2], "Dispersive transport discharge", ylabel="Discharge\n[m3/s]")


def create_plot4(self, axarr, results, color_list):
    times = self.times() / 3600
    # Plot 4
    # Todo: the timeseires is referred as a given name, it does not find it with the . name
    for idx, connector_name in enumerate(self.connector_names):
        if self.upstream_open_boundary and idx == 0:
            axarr[3].plot(
                times,
                results[connector_name + "_M_Up"],
                label="M_uit_" + connector_name,
                linewidth=2,
                color="b",
            )
        else:
            axarr[3].plot(
                times,
                results[connector_name + "_M_Up"],
                label="M_uit_" + connector_name,
                linewidth=2,
                color=color_list[idx],
            )

    axis_settings(
        axarr[3],
        "Total (dispersive and advective) mass flux",
        ylabel="Mass flux\n[kg/s]",
    )


def create_plot5(self, axarr, results, color_list, min_q_plot_threshold):
    times = self.times() / 3600
    # Plot 5
    for idx, connector_name in enumerate(self.connector_names):
        if self.upstream_open_boundary and idx == 0:
            pass
        elif self.downstream_open_boundary and idx == len(self.connector_names) - 1:
            pass
        else:
            axarr[4].plot(
                times,
                results[connector_name + ".HQUp.Q"],
                label="q_adv,mid_from_" + connector_name,
                linewidth=2,
                color=color_list[idx],
            )

    for idx, storage_name in enumerate(self.active_storage_names):
        if (
            abs(sum(self.io.get_timeseries(storage_name + "_qforcing_in")[1]))
            > min_q_plot_threshold
        ):
            axarr[4].plot(
                times,
                self.io.get_timeseries(storage_name + "_qforcing_in")[1],
                label="q_in_" + storage_name,
                linewidth=2,
                linestyle="--",
                color=color_list[idx],
            )
        if (
            abs(sum(self.io.get_timeseries(storage_name + "_qforcing_out")[1]))
            > min_q_plot_threshold
        ):
            axarr[4].plot(
                times,
                -self.io.get_timeseries(storage_name + "_qforcing_out")[1],
                label="q_out_" + storage_name,
                linewidth=2,
                linestyle="--",
                color=color_list[idx],
            )
        plt.yticks(np.arange(-100, 100, 50))

    axis_settings(
        axarr[4],
        "Advective transport discharge",
        ylabel="Discharge\n[m3/s]",
    )


def create_plot6(self, axarr, results, color_list, min_q_plot_threshold):
    times = self.times() / 3600

    # Plot 6
    # Todo: this can only take values outside the mixin...
    empty_plot = True
    for idx, storage_name in enumerate(self.active_storage_names):
        if (
            abs(sum(self.io.get_timeseries(storage_name + "_qforcing_in")[1]))
            > min_q_plot_threshold
        ):
            axarr[5].plot(
                times,
                self.io.get_timeseries(storage_name + "_qforcing_in")[1],
                label="q_in_" + storage_name,
                linewidth=2,
                linestyle="--",
                color=color_list[idx],
            )
            empty_plot = False
        if (
            abs(sum(self.io.get_timeseries(storage_name + "_qforcing_out")[1]))
            > min_q_plot_threshold
        ):
            axarr[5].plot(
                times,
                -self.io.get_timeseries(storage_name + "_qforcing_out")[1],
                label="q_out_" + storage_name,
                linewidth=2,
                linestyle="--",
                color=color_list[idx],
            )
            empty_plot = False
        plt.yticks(np.arange(-100, 100, 50))

    axis_settings(axarr[5], "Extra inflow", ylabel="Discharge\n[m3/s]", empty_plot=empty_plot)


def create_plot7(self, axarr, results, color_list, min_q_plot_threshold):
    times = self.times() / 3600

    # Plot 7
    empty_plot = True
    for idx, storage_name in enumerate(self.active_storage_names):
        if (
            abs(sum(self.io.get_timeseries(storage_name + "_mforcing_in")[1]))
            > min_q_plot_threshold
        ):
            axarr[6].plot(
                times,
                self.io.get_timeseries(storage_name + "_mforcing_in")[1],
                label="m_in_" + storage_name,
                linewidth=2,
                linestyle="--",
                color=color_list[idx],
            )
            empty_plot = False
        if abs(sum(results[storage_name + ".MForcing[2]"])) > min_q_plot_threshold:
            axarr[6].plot(
                times,
                -results[storage_name + ".MForcing[2]"],
                label="m_out_" + storage_name,
                linewidth=2,
                linestyle="--",
                color=color_list[idx],
            )
            empty_plot = False
        # plt.yticks(np.arange(-100, 100, 50))

    axis_settings(axarr[6], "Extra flux", ylabel="mass flux\n[kg/s]", empty_plot=empty_plot)


def create_plot8(self, axarr, results, color_list):
    times = self.times() / 3600

    # Plot 7
    # Todo: maybe here the names are not too generic
    axarr[7].plot(
        times,
        results[self.active_storage_names[0] + "_qforcing_ZSF"],
        label="ZSF up",
        linewidth=2,
        color="b",
    )
    axarr[7].plot(
        times,
        results[self.active_storage_names[-1] + "_qforcing_ZSF"],
        label="ZSF down",
        linewidth=2,
        color="r",
        linestyle="--",
    )
    axarr[7].plot(
        times,
        -results[self.active_storage_names[-1] + "_qforcing_advective"],
        label="downstream_flushing",
        linewidth=2,
        color="g",
        linestyle="--",
    )

    axis_settings(axarr[7], "ZSF and flushing discharge", ylabel="Discharge\n[m3/s]")


def create_plot9(self, axarr, results, color_list):
    times = self.times() / 3600

    # Plot 8
    # Todo: maybe here the names are not too generic
    axarr[8].plot(
        times,
        results[self.active_storage_names[0] + "_mforcing_ZSF"],
        label="ZSF up",
        linewidth=2,
        color="b",
    )
    axarr[8].plot(
        times,
        results[self.active_storage_names[-1] + "_mforcing_ZSF"],
        label="ZSF down",
        linewidth=2,
        color="r",
        linestyle="--",
    )
    axarr[8].plot(
        times,
        -results[self.active_storage_names[-1] + ".MForcing[4]"],
        label="downstream_flushing",
        linewidth=2,
        color="g",
        linestyle="--",
    )

    ymin, ymax = axarr[8].get_ylim()
    plt.sca(axarr[8])
    plt.yticks([0.0, np.round(ymax / 2, -1)])

    axis_settings(
        axarr[8],
        "ZSF and flushing flux",
        ylabel="Mass flux\n[kg/s]",
    )


def create_plot10(self, axarr, results, color_list):
    times = self.times() / 3600

    # Plot 8
    axarr[9].plot(
        times,
        self.io.get_timeseries("upstream_discharge")[1],
        label="up",
        linewidth=2,
        color="b",
    )
    axarr[9].plot(
        times,
        self.io.get_timeseries("downstream_discharge")[1],
        label="down",
        linewidth=2,
        color="r",
        linestyle="--",
    )
    axarr[9].set_ylabel("Discharge\n[m3/s]")
    ymin, ymax = axarr[9].get_ylim()
    plt.sca(axarr[9])
    plt.yticks([0.0, np.round(ymax / 2, -1)])

    axis_settings(
        axarr[9],
        "Discharge boundaries",
        ylabel="Discharge\n[m3/s]",
    )


def create_plot11(self, axarr, results, color_list):
    times = self.times() / 3600

    # Plot 10
    axarr[10].plot(
        times,
        self.io.get_timeseries("head_sea_upstream_zsf")[1],
        label="up",
        linewidth=2,
        color="b",
    )
    axarr[10].plot(
        times,
        self.io.get_timeseries("head_sea_downstream_zsf")[1],
        label="down",
        linewidth=2,
        color="r",
        linestyle="--",
    )
    ymin, ymax = axarr[10].get_ylim()
    plt.sca(axarr[10])
    plt.yticks([0.0, np.round(ymax / 2, 0)])

    axis_settings(
        axarr[10],
        "ZSF discharge boundaries",
        ylabel="Head\n[m]",
    )


def create_plot12(self, axarr, results, color_list):
    times = self.times() / 3600

    # Plot 10
    axarr[11].plot(
        times,
        self.io.get_timeseries("salinity_sea_upstream_zsf")[1],
        label="up",
        linewidth=2,
        color="b",
    )
    axarr[11].plot(
        times,
        self.io.get_timeseries("salinity_sea_downstream_zsf")[1],
        label="down",
        linewidth=2,
        color="r",
        linestyle="--",
    )
    ymin, ymax = axarr[11].get_ylim()
    plt.sca(axarr[11])
    plt.yticks([0.0, np.round(ymax / 2, 0)])

    axis_settings(
        axarr[11],
        "ZSF concentration boundaries",
        ylabel="Salinity\n[-]",
    )


class SaltSimulationMixin:
    """
    Class for simulating advective and convective salt trasnport.
    """

    def initialize(self):
        """This run is initialized.

        The initital middle discharge is set to zero and volumes are calculted from initial level.

        """
        for name in self.connector_names:
            self.set_var(name + "_middle_discharge", 0.0)

        parameters = self.parameters()
        for storage_name in self.storage_names:
            level = self._CSVMixin__initial_state[storage_name + "_level"]
            self._CSVMixin__initial_state[storage_name + ".V"] = (
                level - parameters[storage_name + ".H_b"]
            ) * parameters[storage_name + ".A"]

        super().initialize()

    def read(self):
        """This part is reading the input file.

        If the input file is in csv format, the date format is automatically adjusted.

        """
        input_database = pd.read_csv(
            self._input_folder + "/timeseries_import.csv", parse_dates=True, index_col=[0]
        )
        input_database.to_csv(
            self._input_folder + "/timeseries_import.csv", date_format="%Y-%m-%d %H:%M:%S"
        )
        print("Changed timeseries input format.")
        super().read()

    def update(self, dt):
        """Upate step.

        In this section the convective discharges are set depending on which closing term is chosen.

        """
        if dt < 0:
            dt = self.get_time_step()
        time_step = self.get_current_time() / dt

        q_forcing = np.zeros(len(self.active_storage_names))
        for idx, name in enumerate(self.active_storage_names):
            q_forcing[idx] = (
                self.io.get_timeseries(name + "_qforcing_in")[1][int(time_step + 1)]
                + self.io.get_timeseries(name + "_qforcing_out")[1][int(time_step + 1)]
            )

        net_q_system = np.sum(self.ZSF_Q) + np.sum(q_forcing)
        net_q_storages = q_forcing.copy()
        net_q_storages[0] += self.ZSF_Q[0]
        net_q_storages[-1] += self.ZSF_Q[1]

        if self.water_level_closing:
            set_mid_q_wl_closing(self, net_q_storages, net_q_system)
        elif self.discharge_closing:
            set_mid_q_q_closing(self, net_q_storages, net_q_system)

        super().update(dt)

    def extra_equations(self):
        """All necessary extra equations are added.

        These extra equations connect the dispersive discharges to the blocks.
        """
        equations = super().extra_equations()
        self.equation_list = []

        add_equations_middle_q_m(self)
        add_equations_forcings(self)
        add_equations_zsf(self)

        equations += self.equation_list
        return equations

    def get_output_variables(self):
        """This section adds extra output variables."""

        variables = super().get_output_variables().copy()

        for idx, name in enumerate(self.active_storage_names):
            variables.extend([name + ".MForcing[2]"])
            if idx in {0, len(self.active_storage_names) - 1}:
                variables.extend([name + "_qforcing_ZSF"])
                variables.extend([name + "_mforcing_ZSF"])
                variables.extend([name + "_qforcing_advective"])
                variables.extend([name + ".MForcing[4]"])

        for name in self.connector_names:
            variables.extend([name + ".flux_q1_s1"])
            variables.extend([name + ".HQUp.Q"])

        for name in self.storage_names:
            variables.extend([name + ".V"])

        return variables

    def post(self):
        super().post()

        results = self.extract_results()
        np.set_printoptions(suppress=True)
        min_q_plot_threshold = 0.0001
        color_list = [
            "darkviolet",
            "orange",
            "green",
            "magenta",
            "yellow",
            "deepskyblue",
            "black",
            "forestgreen",
            "brown",
            "pink",
        ]
        f, axarr = plt.subplots(12, sharex=True)
        plt.subplots_adjust(left=0.1, bottom=0.1, top=0.95, wspace=0.4, hspace=0.85)
        times = self.times() / 3600

        create_plot1(self, axarr, results, color_list)
        create_plot2(self, axarr, results, color_list)
        create_plot3(self, axarr, results, color_list)
        create_plot4(self, axarr, results, color_list)
        create_plot5(self, axarr, results, color_list, min_q_plot_threshold)
        create_plot6(self, axarr, results, color_list, min_q_plot_threshold)
        create_plot7(self, axarr, results, color_list, min_q_plot_threshold)
        create_plot8(self, axarr, results, color_list)
        create_plot9(self, axarr, results, color_list)
        create_plot10(self, axarr, results, color_list)
        create_plot11(self, axarr, results, color_list)
        create_plot12(self, axarr, results, color_list)

        axarr[-1].set_xlabel("Time [h]")
        f.autofmt_xdate()
        for ax in axarr:
            ax.set_xlim(min(times), max(times))

        # Shrink each axis by 20% and put a legend to the right of the axis
        for i in range(len(axarr)):
            box = axarr[i].get_position()
            axarr[i].set_position([box.x0, box.y0, box.width * 0.8, box.height])
            if len(axarr[i].get_lines()) > 0:
                axarr[i].legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)

        # Output Plot
        f.set_size_inches(8, 12)

        plt.savefig(
            os.path.join(self._output_folder, "overall_results.png"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=300,
        )

        pd.read_csv("..\\output\\timeseries_export.csv")
