import os

import autokeras as ak
from AbstractAdapter import AbstractAdapter
from AdapterUtils import (export_model, prepare_tabular_dataset,
                          read_tabular_dataset_training_data)
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
        self.df, test = self.__data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        reg = ak.StructuredDataRegressor(overwrite=True,
                                         max_trials=self._max_iter,
                                         # metric=self._configuration['metric'],
                                         directory=self._result_path,
                                         seed=42)
        reg.fit(x=X, y=y)
        self.__export_model(reg, self._configuration["session_id"], 'model_keras.p')

    @staticmethod
    def __data_loader(config):
        train_data = None
        test_data = None

        if config["task"] == 1:
            train_data, test_data = read_tabular_dataset_training_data(config)
        elif config["task"] == 2:
            train_data, test_data = read_tabular_dataset_training_data(config)
        elif config["task"] == 3:
            train_data, test_data = None
        elif config["task"] == 4:
            train_data, test_data = None
        elif config["task"] == 5:
            train_data, test_data = None

        return train_data, test_data
