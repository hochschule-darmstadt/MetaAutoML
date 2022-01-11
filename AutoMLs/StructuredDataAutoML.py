import os
import pandas as pd
import pickle
from flaml import AutoML

from enum import Enum, unique

from JsonUtil import get_config_property

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

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])
        target = self.__configuration["tabular_configuration"]["target"]["target"]
        self.__X = df.drop(target, axis=1)
        self.__y = df[target]

    def __dataset_preparation(self):
        for column, dt in self.__configuration["tabular_configuration"]["features"].items():
            if DataType(dt) is DataType.DATATYPE_IGNORE:
                self.__X = self.__X.drop(column, axis=1)
            elif DataType(dt) is DataType.DATATYPE_CATEGORY:
                self.__X[column] = self.__X[column].astype('category')
            elif DataType(dt) is DataType.DATATYPE_BOOLEAN:
                self.__X[column] = self.__X[column].astype('bool')
            elif DataType(dt) is DataType.DATATYPE_INT:
                self.__X[column] = self.__X[column].astype('int')
            elif DataType(dt) is DataType.DATATYPE_FLOAT:
                self.__X[column] = self.__X[column].astype('float')
        self.__cast_target()

    def __cast_target(self):
        target_dt = self.__configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_CATEGORY:
            self.__y = self.__y.astype('category')
        elif DataType(target_dt) is DataType.DATATYPE_BOOLEAN:
            self.__y = self.__y.astype('bool')
        elif DataType(target_dt) is DataType.DATATYPE_INT:
            self.__y = self.__y.astype('int')
        elif DataType(target_dt) is DataType.DATATYPE_FLOAT:
            self.__y = self.__y.astype('float')

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open(os.path.join(get_config_property('output-path'), 'model_flaml.p'), 'wb') as file:
            pickle.dump(model, file)

    def execute_task(self):
        """
        Execute the ML task
        """
        if self.__configuration["task"] == 1:
            self.__classification()
        elif self.__configuration["task"] == 2:
            self.__regression()

    def __generate_settings(self):
        automl_settings = {"log_file_name": 'flaml.log'}
        if self.__configuration["runtime_constraints"]["runtime_limit"] != 0:
            automl_settings.update({"time_budget": self.__configuration["runtime_constraints"]["runtime_limit"]})
        if self.__configuration["runtime_constraints"]["max_iter"] != 0:
            automl_settings.update({"max_iter": self.__configuration["runtime_constraints"]["max_iter"]})
        return automl_settings

    def __classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        self.__dataset_preparation()
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "metric": 'accuracy',
            "task": 'classification',
        })

        automl.fit(X_train=self.__X, y_train=self.__y, **automl_settings)
        self.__export_model(automl)

    def __regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        self.__dataset_preparation()
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "metric": 'rmse',
            "task": 'regression',
        })

        automl.fit(X_train=self.__X, y_train=self.__y, **automl_settings)
        self.__export_model(automl)
