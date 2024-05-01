from typing import Union

import numpy as np
import pandas as pd


def read_reservoir_data(
    reservoirs_csv_path,
    volume_level_csv_path,
    volume_area_csv_path,
    spillwaydischarge_csv_path=None,
):
    r"""
    This function reads the CSV files provided as input and converts the
    reservoir data, volume-level tables, volume-area tables and the spillway
    -discharge table to dataFrames. Optional: Add interpolated volume
    setpoints corresponding to provided reservoir levels, ie. 'surcharge',
    'fullsupply','crestheight' (to be provided in reservoirs_csv_path), to the
    dataFrames.

    Parameters
    ----------
    reservoirs_csv_path :
        Path to csv file that contains the properties (columns) of the
        reservoirs, such as Name, surcharge, fullsupply, crestheight,
        volume_min, volume_max, q_turbine_max, q_spill_max

    volume_level_csv_path :
        Path to csv file that contains the columns ReservoirName, Storage_m3,
        Elevation_m

    volume_area_csv_path :
        Path to csv file that contains the columns ReservoirName, Storage_m3,
        Area_m2

    spillwaydischarge_csv_path :
        Optionally: Path to csv file that contains the columns ReservoirName,
        Elevation_m, Discharge_m3s

    Returns
    -------
    reservoirs :
        A dictionary of lookup tables for the reservoir with, if provided,
        volume setpoints
    """

    res_df = pd.read_csv(reservoirs_csv_path, sep=None, index_col=0, engine="python")
    vh_data_df = pd.read_csv(volume_level_csv_path, sep=None, index_col=0, engine="python")
    va_data_df = pd.read_csv(volume_area_csv_path, sep=None, index_col=0, engine="python")
    # read spill spillway-discharge table if provided
    try:
        spillwaydischarge_df = pd.read_csv(
            spillwaydischarge_csv_path, sep=None, index_col=0, engine="python"
        )
        spillwaydischarge = True
    except BaseException:
        spillwaydischarge = False

    # Make dictionary with reservoir data
    reservoirs = {}
    for index, _row in res_df.iterrows():
        if spillwaydischarge:
            reservoirs[index] = Reservoir(
                index,
                vh_data_df.loc[index],
                va_data_df.loc[index],
                res_df.loc[index],
                spillwaydischarge_df.loc[index],
            )
        else:
            reservoirs[index] = Reservoir(
                index, vh_data_df.loc[index], va_data_df.loc[index], res_df.loc[index]
            )
        # compute setpoints as volumes, using the vh_data_df if user gives
        # setpoints in res_df.
        for key in ["surcharge", "fullsupply", "crestheight"]:
            if key in res_df.keys():
                print(key)
                reservoirs[index].set_v_setpoints(key)
    return reservoirs


class Reservoir:
    r"""
    Reservoir class

    Attributes:
    -----------
    name : str
        Name of the reservoir
    properties : Series
        properties of the reservoirs, such as Name, surcharge, fullsupply,
        crestheight, volume_min, volume_max, q_turbine_max, q_spill_max
    v_setpoints : dict
        Optionally: dictionary with keys 'surcharge', 'fullsupply',
        'crestheight'

    __vh_lookup : DataFrame
        volume-level lookup table

    __va_lookup : DataFrame
        volume-area lookup table

    __spillwaydischargelookup : DataFrame
        Optionally: spillway-discharge lookup table
    Methods:
    --------
    """

    def __init__(self, name, vh_data, va_data, reservoir_properties, spillwaydischargedata=None):
        self.name = name
        self.__vh_lookup = vh_data
        self.__va_lookup = va_data
        self.properties = reservoir_properties
        self.__spillwaydischargelookup = spillwaydischargedata
        self.v_setpoints = {}

    def level_to_volume(self, levels: Union[float, np.ndarray]):
        r"""
        Returns the reservoir storage volume(s) by one-dimensional linear
        interpolation for a given reservoir elevation-storage table.

        Parameters
        ----------
        levels :
            Water level(s)

        Returns
        -------
        volumes :
             Reservoir  volume(s)
        """
        volumes = np.interp(levels, self.__vh_lookup["Elevation_m"], self.__vh_lookup["Storage_m3"])
        return volumes

    def volume_to_level(self, volumes: Union[float, np.ndarray]):
        r"""
        Returns the water level(s) in the reservoir by one-dimensional linear
        interpolation for a given reservoir storage-elevation table.

        Parameters
        ----------
        volumes :
            Reservoir storage volume(s)

        Returns
        -------
        levels :
            Water level(s)
        """
        levels = np.interp(volumes, self.__vh_lookup["Storage_m3"], self.__vh_lookup["Elevation_m"])
        return levels

    def volume_to_area(self, volumes: Union[float, np.ndarray]):
        r"""
        Returns the area(s) of the reservoir by one-dimensional linear
        interpolation for a given reservoir storage-area table.

        Parameters
        ----------
        volumes :
            Reservoir storage volume(s)

        Returns
        -------
        areas :
            Reservoir area(s)
        """
        areas = np.interp(volumes, self.__va_lookup["Storage_m3"], self.__va_lookup["Area_m2"])
        return areas

    def level_to_area(self, levels: Union[float, np.ndarray]):
        r"""
        Returns the area(s) of the reservoir in two steps. First, one-
        dimensional linear interpolation for given level-volume table to get
        the corresponding volume. Next, the area by one-dimensional linear
        interpolation for a given storage-area table.

        Parameters
        ----------
        levels :
            Water level(s)

        Returns
        -------
        areas :
            Reservoir area(s)
        """
        volume_interp = np.interp(
            levels, self.__vh_lookup["Elevation_m"], self.__vh_lookup["Storage_m3"]
        )
        areas = np.interp(
            volume_interp, self.__va_lookup["Storage_m3"], self.__va_lookup["Area_m2"]
        )
        return areas

    def volume_to_spillwaydischarge(self, volumes: Union[float, np.ndarray]):
        r"""
        Returns the spillway discharge in two steps. First, one-dimensional
        linear interpolation for a given volume-level table to get the
        corresponding level. Next, the spillway discharge by one-dimensional
        linear interpolation for a given elevation-discharge table.

        Parameters
        ----------
        volumes :
            Reservoir storage volume(s)

        Returns
        -------
        spillwaydischarge :
            Spillway discharge
        """
        levels = self.volume_to_level(volumes)
        spillwaydischarge = np.interp(
            levels,
            self.__spillwaydischargelookup["Elevation_m"],
            self.__spillwaydischargelookup["Discharge_m3s"],
        )
        return spillwaydischarge

    def set_v_setpoints(self, level: str):
        r"""
        Add interpolated volume setpoints for defined setpoint levels to
        v_setpoints dictionary.

        Parameters
        ----------
        level:
            Setpoint level
        """
        self.v_setpoints[level] = self.level_to_volume(self.properties[level])
