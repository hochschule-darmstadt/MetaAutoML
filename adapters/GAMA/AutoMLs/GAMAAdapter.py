import os

from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property


from predict_time_sources import feature_preparation

import json
import pickle
from gama import GamaClassifier

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
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        # TODO: add params
        automl = GamaClassifier(max_total_time=180, store="nothing", n_jobs=1)
        automl.fit(X, y)

        export_model(automl, self._configuration["result_folder_location"], 'GAMA.p')


        return



