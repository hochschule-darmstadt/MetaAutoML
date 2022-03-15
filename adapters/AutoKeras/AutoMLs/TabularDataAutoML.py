import os
import dill
import pandas as pd
import autokeras as ak

from enum import Enum, unique
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
        super(TabularDataAutoML, self).__init__(configuration)

        # if not self.__configuration.keys().__contains__("metric") or self.__configuration["metric"] == "":
            # handle empty metric field, None is the default metric parameter for AutoKeras
            # self.__configuration["metric"] = None
            
    def __cast_target(self):
        target_dt = self._configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_CATEGORY or \
                DataType(target_dt) is DataType.DATATYPE_BOOLEAN or \
                DataType(target_dt) is DataType.DATATYPE_INT:
            self._y = self._y.astype('int')
        elif DataType(target_dt) is DataType.DATATYPE_FLOAT:
            self._y = self._y.astype('float')

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open(os.path.join(get_config_property('output-path'), 'tmp', 'model_keras.p'), 'wb+') as file:
            dill.dump(model, file)

    def execute_task(self):
        """Execute the ML task"""
        if self._configuration["task"] == 1:
            self.__classification()
        elif self._configuration["task"] == 2:
            self.__regression()

    def __classification(self):
        """Execute the classification task"""
        self._read_training_data()
        self._dataset_preparation()
        clf = ak.StructuredDataClassifier(overwrite=True,
                                          max_trials=self._max_iter,
                                          # metric=self._configuration['metric'],
                                          seed=42)
        clf.fit(x=self._X, y=self._y)
        self.__export_model(clf)

    def __regression(self):
        """Execute the regression task"""
        self._read_training_data()
        self._dataset_preparation()
        reg = ak.StructuredDataRegressor(overwrite=True,
                                         max_trials=self._max_iter,
                                         # metric=self._configuration['metric'],
                                         seed=42)
        reg.fit(x=self._X, y=self._y)
        self.__export_model(reg)
