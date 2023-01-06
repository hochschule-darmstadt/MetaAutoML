import os

from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from JsonUtil import get_config_property

# TODO implement
class EvalMLAdapter:
    """Implementation of the AutoML functionality for EvalML

    Args:
        AbstractAdapter (_type_): _description_
    """

    def __init__(self, configuration: dict):
        """Init a new instance of EvalMLAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30

    def start(self):
        """Start the correct ML task functionality of EvalML"""
        raise NotImplementedError("Correct ML task should be implemented!")
