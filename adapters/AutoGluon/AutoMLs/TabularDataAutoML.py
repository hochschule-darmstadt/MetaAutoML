import os
import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor
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
        self._output_path = os.path.join(get_config_property('output-path'),
                                          'tmp',
                                          'model_gluon.gluon')

    def execute_task(self):
        """
        Execute the ML task
        NOTE: AutoGLUON automatically saves the model in a file
        Therefore we do not need to export it using pickle
        """
        if self._configuration["task"] == 1:
            self.__classification()
        elif self._configuration["task"] == 2:
            self.__regression()

    def __classification(self):
        """
        Execute the classification task
        """
        self._read_training_data()
        self._dataset_preparation()
        data = self._X
        data[self._target] = self._y
        model = TabularPredictor(label=self._target,
                                 problem_type="multiclass",
                                 path=self._output_path).fit(
            data,
            time_limit=self._time_limit)

    def __regression(self):
        """
        Execute the regression task
        """
        self._read_training_data()
        self._dataset_preparation()
        data = self._X
        data[self._target] = self._y
        model = TabularPredictor(label=self._target,
                                 problem_type="regression",
                                 path=self._output_path).fit(
            data,
            time_limit=self._time_limit)
