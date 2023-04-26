import os

from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property


from predict_time_sources import feature_preparation

import json
import pickle

# TODO implement
class GAMAAdapter:
    """Implementation of the AutoML functionality for GAMA

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
        """Start the correct ML task functionality of GAMA"""
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__classification()

    def __classification(self):
        """Execute the tabular classification task and export the found model"""
        return



