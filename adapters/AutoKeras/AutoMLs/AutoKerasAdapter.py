import os

import autokeras as ak
import tensorflow as tf
from AbstractAdapter import AbstractAdapter
from AdapterUtils import (export_model, prepare_tabular_dataset,
                          read_tabular_dataset_training_data)
from DataLoader import data_loader
from JsonUtil import get_config_property


class AutoKerasAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for AutoKeras
    """
    def __init__(self, configuration: dict):
        """
        Init a new instance of AutoKerasAdapter
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        super(AutoKerasAdapter, self).__init__(configuration)
        self._result_path = os.path.join(get_config_property("output-path"), self._configuration["session_id"])

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == 1:
                self.__tabular_classification()
            elif self._configuration["task"] == 2:
                self.__tabular_regression()
            elif self._configuration["task"] == 3:
                self.__tabular_classification()
            elif self._configuration["task"] == 4:
                self.__image_classification()
            elif self._configuration["task"] == 5:
                self.__image_regression()

    def __tabular_classification(self):
        """Execute the classification task"""

        self.df, test = self.__data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        clf = ak.StructuredDataClassifier(overwrite=True,
                                          max_trials=self._max_iter,
                                          # metric=self._configuration['metric'],
                                          directory=self._result_path,
                                          seed=42)
                                          
        clf.fit(x=X, y=y)
        export_model(clf, self._configuration["session_id"], 'model_keras.p')

    def __tabular_regression(self):
        """Execute the regression task"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        reg = ak.StructuredDataRegressor(overwrite=True,
                                         max_trials=self._max_iter,
                                         # metric=self._configuration['metric'],
                                         directory=self._result_path,
                                         seed=42)

        reg.fit(x=X, y=y)
        export_model(reg, self._configuration["session_id"], 'model_keras.p')

    def __image_classification(self):
        """"Execute image classification task"""

        train_data, test_data = data_loader(self._configuration)

        clf = ak.ImageClassifier(overwrite=True, 
                                max_trials=self._configuration["runtime_constraints"]["max_iter"],
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._result_path)

        clf.fit(train_data, epochs=self._configuration["runtime_constraints"]["epochs"])

        export_model(clf, self._configuration["session_id"], 'model_keras.p')

    def __image_regression(self):
        """Execute image regression task"""

        train_data, test_data = data_loader(self._configuration)

        reg = ak.ImageRegressor(overwrite=True, 
                                max_trials=self._configuration["runtime_constraints"]["max_iter"],
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._result_path)
                                
        reg.fit(train_data, epochs=self._configuration["runtime_constraints"]["epochs"])

        export_model(reg, self._configuration["session_id"], 'model_keras.p')

