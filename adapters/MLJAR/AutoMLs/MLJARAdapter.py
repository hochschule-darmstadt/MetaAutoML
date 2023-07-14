import os
import shutil
import MLJARParameterConfig as mjpc

from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property
from supervised.automl import AutoML
from MLJARWrapper import MLJARWrapper

class MLJARAdapter:
    """
    Implementation of the AutoML functionality for MLJAR
    """

    def __init__(self, configuration: dict):
        """Init a new instance of MLJARAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30
        #Create correct output folder for current training


    def start(self):
        """Start the correct ML task functionality of AutoKeras"""
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__tabular_classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__tabular_regression()

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        result_path = self._configuration["model_folder_location"]
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), mjpc.task_config)
        automl = AutoML(total_time_limit=self._configuration["configuration"]["runtime_limit"], mode="Compete", **parameters, results_path=result_path)
        automl.fit(X, y)
        shutil.copytree(self._configuration["model_folder_location"], os.path.join(self._configuration["result_folder_location"], "Models"))
        export_model(MLJARWrapper(automl, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""
        result_path = self._configuration["model_folder_location"]
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        automl = AutoML(total_time_limit=self._configuration["configuration"]["runtime_limit"], mode="Compete", results_path=result_path)
        automl.fit(X, y)
        shutil.copytree(self._configuration["model_folder_location"], os.path.join(self._configuration["result_folder_location"], "Models"))
