import os

from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from AdapterUtils import *
from JsonUtil import get_config_property

import evalml
from evalml import AutoMLSearch
from evalml.objectives import FraudCost

import pandas as pd
from predict_time_sources import feature_preparation, DataType, SplitMethod

import json
import pickle

# TODO implement
class EvalMLAdapter:
    """Implementation of the AutoML functionality for EvalML

    Args:
        AbstractAdapter (_type_): _description_
    """

    def __init__(self, configuration: dict):
        """Init a new instance of EvalMLAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30

    def start(self):
        """Start the correct ML task functionality of EvalML"""
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__regression()
            elif self._configuration["configuration"]["task"] == ":text_classification":
                self.__classification()
            elif self._configuration["configuration"]["task"] == ":text_regression":
                self.__regression()

    def __classification(self):
        """Execute the tabular classification task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        classification_type = "binary" if y.nunique() == 2 else "multiclass"
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type=classification_type,
                    objective="auto",
                    max_batches=3,
                    verbose=False,
                )
        automl.search()
        automl.describe_pipeline(3)
        best_pipeline_tobe_export = automl.best_pipeline
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')
        

    def __regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        print(type(X))
        problem_type = "REGRESSION"
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type=problem_type,
                    objective="auto",
                    max_batches=3,
                    verbose=False,
                )
        automl.search()
        automl.describe_pipeline(3)
        best_pipeline_tobe_export = automl.best_pipeline
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')
