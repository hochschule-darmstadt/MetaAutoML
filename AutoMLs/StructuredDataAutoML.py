import os
import pickle

import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor

from enum import Enum, unique


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
        # set default values
        if self.__configuration["time_budget"] == 0:
            self.__configuration["time_budget"] = 20
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
		In case of AutoGluon only provide the training file path
        """
        self.__training_data = pd.read_csv(
            os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]))

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML +model
        """
        with open('templates/output/gluon-model.p', 'wb') as file:
            pickle.dump(model, file)

    def __feature_selection(self):
        for column, dt in self.__configuration["configuration"]["features"].items():
            if DataType(dt) is DataType.DATATYPE_IGNORE:
                self.__training_data = self.__training_data.drop(column, axis=1)
            elif DataType(dt) is DataType.DATATYPE_CATEGORY:
                self.__training_data[column] = self.__training_data[column].astype('category')

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
        target = self.__configuration["configuration"]["target"]
        model = TabularPredictor(label=target, problem_type="multiclass", path="templates/output/model_autogluon").fit(
            self.__training_data,
            time_limit=
            self.__configuration[
                "time_budget"])
        self.__export_model(model)

    def __regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        target = self.__configuration["configuration"]["target"]
        model = TabularPredictor(label=target, problem_type="regression", path="templates/output/model_autogluon").fit(
            self.__training_data,
            time_limit=
            self.__configuration[
                "time_budget"])
        self.__export_model(model)
