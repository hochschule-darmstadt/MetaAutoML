import os
import pickle
import sys

import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor
from enum import Enum, unique

from JsonUtil import get_config_property


@unique
class DataType(Enum):
    DATATYPE_UNKNOWN = 0
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
        self.target = self.__configuration["tabular_configuration"]["target"]["target"]

        # set default values
        if self.__configuration["runtime_constraints"]["runtime_limit"] == 0:
            self.__configuration["runtime_constraints"]["runtime_limit"] = 20

    def __read_training_data(self):
        """
        Read the training dataset from disk
        In case of AutoGluon only provide the training file path
        """
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])
        self.__X = df.drop(self.target, axis=1)
        self.__y = df[self.target]

    def __dataset_preparation(self):
        for column, dt in self.__configuration["tabular_configuration"]["features"].items():
            if DataType(dt) is DataType.DATATYPE_IGNORE:
                self.__X = self.__X.drop(column, axis=1)
            elif DataType(dt) is DataType.DATATYPE_CATEGORY:
                self.__X[column] = self.__X[column].astype('category')
        # cast target to a different datatype if necessary
        self.__cast_target()

    def __cast_target(self):
        target_dt = self.__configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_CATEGORY:
            self.__y = self.__y.astype('category')
        elif DataType(target_dt) is DataType.DATATYPE_BOOLEAN:
            self.__y = self.__y.astype('bool')

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML +model
        """
        output_path = os.path.join(get_config_property('output-path'),
                                   'model_gluon.p')
        with open(output_path, 'wb') as file:
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
        self.__dataset_preparation()
        data = self.__X
        data[self.target] = self.__y
        model = TabularPredictor(label=self.target,
                                 problem_type="multiclass",
                                 path="templates/output/model_autogluon").fit(
            data,
            time_limit=self.__configuration["runtime_constraints"]["runtime_limit"])
        self.__export_model(model)

    def __regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        self.__dataset_preparation()
        data = self.__X
        data[self.target] = self.__y
        model = TabularPredictor(label=self.target,
                                 problem_type="regression",
                                 path="templates/output/model_autogluon").fit(
            data,
            time_limit=self.__configuration["runtime_constraints"]["runtime_limit"])
        self.__export_model(model)
