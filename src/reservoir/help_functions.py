import logging
import numpy as np

logger = logging.getLogger("rtctools")


def SetQ(self, target_variable: str, target_type: str, indicator='MEAN', target_data=None, t=None, option=None):
    """
    The discharge from the reservoir for the time period is known beforehand and the pool elevation is the only computed quantity
    Parameters
    ----------
    target_variable : str
        The variable that is to be set

    target_data : str
        the name of the target data. If not provided, it is set to the name of the target_varaible

    target_type : str
        The type of target data. either 'timeseries' or 'parameter'
    
    t:
        The time from which the target data should be read at if of type timeseries, the defualt is the current time of the simulation run
        
    option:
        the user can indicate the action to be take if missing values are found
        'MEAN': can be used in combination with target_type = 'timeseries' and indiacator = 'INST'. It will take the mean of the timeseries excluding nans
        'PREVIOUS': can be used in combination with target_type = 'timeseries' and indiacator = 'INST'

    """

    if target_data is None:
        target_data = target_variable
    if t is None and target_type == 'timeseries' and indicator == 'INST':
        t = self.get_time_step()
    if target_type == 'timeseries':
        if indicator == 'INST':
            target_value = self.get_timeseries(target_data)[t]
            if np.isnan(target_value):
                if option is None:
                    logger.error('SetQ detects a nan at time {} in target data {} when setting {} and there is no option set to treat this.'.format(t, target_data, target_variable))
                elif option == 'MEAN':
                    target_value = np.nanmean(self.get_timeseries(target_data))
                elif option == 'PREVIOUS':
                    i=0
                    while np.isnan(target_value):
                        if i >=0:
                            target_value = self.get_timeseries(target_data)[t-i]
                            i+=1
                        else:
                            logger.error('SetQ: There is no previous non-empty value in timeseries {}'.format(target_data))
                            break
        elif indicator == 'MEAN':
            target_value = np.mean(self.get_timeseries(target_data))
        
        self.set_var(target_variable, target_value)
    elif target_type == 'parameter':
        target_value = self.io.get_parameters()[target_data]
        if np.isnan(target_value):
            if option is None:
                logger.error('SetQ detects a nan at time {} in target data {} when setting {} and there is no option set to treat this.'.format(t, target_data, target_variable))
        self.set_var(target_variable, target_value)


def SetMin(self, model_output_type: list, target_variable: str):
    """
    Use minimum value of already computed outputs
    """
    if not set(model_output_type).issubset(["INST", "MEAN", "POOL"]):
        logger.error(
            "SetMin function does not support model output type {}.".format(
                model_output_type
            )
        )
    min_value = np.nan
    for output_type in model_output_type:
        if output_type == "INST":
            var_name = target_variable
            min_value = np.nanmin(self.get_var(var_name), min_value)
        if output_type == "MEAN":
            var_name = target_variable
            min_value = np.nanmin(self.get_timeseries(var_name), min_value)
        if output_type == "POOL":
            var_name = target_variable
            min_value = np.nanmin(self.get_var(var_name), min_value)

    self.set_var("target_variable", min_value)