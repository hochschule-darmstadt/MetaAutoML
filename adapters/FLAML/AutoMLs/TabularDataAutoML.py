import os
import pandas as pd
import pickle
from flaml import AutoML

from JsonUtil import get_config_property
from predict_time_sources import feature_preparation, DataType, SplitMethod
from AbstractTabularDataAutoML import AbstractTabularDataAutoML

class TabularDataAutoML(AbstractTabularDataAutoML):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of TabularDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        super().__init__(configuration)

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open(os.path.join(get_config_property('output-path'), 'tmp', 'model_flaml.p'), 'wb+') as file:
            pickle.dump(model, file)

    def execute_task(self):
        """
        Execute the ML task
        """
        if self._configuration["task"] == 1:
            self.__classification()
        elif self._configuration["task"] == 2:
            self.__regression()

    def __generate_settings(self):
        automl_settings = {"log_file_name": 'flaml.log'}
        if self._configuration["runtime_constraints"]["runtime_limit"] != 0:
            automl_settings.update({"time_budget": self._configuration["runtime_constraints"]["runtime_limit"]})
        if self._configuration["runtime_constraints"]["max_iter"] != 0:
            automl_settings.update({"max_iter": self._configuration["runtime_constraints"]["max_iter"]})
        return automl_settings

    def __classification(self):
        """
        Execute the classification task
        """
        self._read_training_data()
        self._dataset_preparation()
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "metric": self._configuration["metric"] if self._configuration["metric"] != "" else 'accuracy',
            "task": 'classification',
        })

        automl.fit(X_train=self._X, y_train=self._y, **automl_settings)
        self.__export_model(automl)

    def __regression(self):
        """
        Execute the regression task
        """
        self._read_training_data()
        self._dataset_preparation()
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "metric": self._configuration["metric"] if self._configuration["metric"] != "" else 'rmse',
            "task": 'regression',
        })

        automl.fit(X_train=self._X, y_train=self._y, **automl_settings)
        self.__export_model(automl)
