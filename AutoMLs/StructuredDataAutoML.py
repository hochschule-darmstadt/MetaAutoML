import os
import pandas as pd
import pickle
from flaml import AutoML

from enum import Enum, unique


@unique
class DataType(Enum):
    DATATYPE_UNKNOW = 0
    DATATYPE_STRING = 1
    DATATYPE_INT = 2
    DATATYPE_FLOAT = 3
    DATATYPE_CATEGORY = 4
    DATATYPE_BOOLEAN = 5
    DATATYPE_DATETIME = 6
    DATATYPE_IGNORE = 7


class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        self.__configuration = configuration
        # set default values
        if self.__configuration["time_budget"] == 0:
            self.__configuration["time_budget"] = 20

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]))
        self.__X = df.drop(self.__configuration["configuration"]["target"], axis=1)
        self.__y = df[self.__configuration["configuration"]["target"]]

    def __feature_selection(self):
        for column, type in self.__configuration["configuration"]["features"].items():
            if DataType(type) is DataType.DATATYPE_IGNORE:
                self.__X = self.__X.drop(column, axis=1)

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open('templates/output/flaml-model.p', 'wb') as file:
            pickle.dump(model, file)

    def execute_task(self):
        """
        Execute the ML task
        """
        if self.__configuration["task"] == 1:
            self.__classification()
        elif self.__configuration["task"] == 2:
            self.__regression()

    def __classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        self.__feature_selection()
        automl = AutoML()
        automl_settings = {
            "time_budget": self.__configuration["time_budget"],
            "metric": 'accuracy',
            "task": 'classification',
            "log_file_name": 'flaml.log',
        }

        automl.fit(X_train=self.__X, y_train=self.__y, **automl_settings)
        self.__export_model(automl)

    def __regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        self.__feature_selection()
        automl = AutoML()
        automl_settings = {
            "time_budget": self.__configuration["time_budget"],
            "metric": 'rmse',
            "task": 'regression',
            "log_file_name": 'flaml.log',
        }

        automl.fit(X_train=self.__X, y_train=self.__y, **automl_settings)
        self.__export_model(automl)
