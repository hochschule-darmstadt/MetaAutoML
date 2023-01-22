import os

from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from AdapterUtils import *
from JsonUtil import get_config_property

import evalml
from evalml import AutoMLSearch
from evalml.objectives import FraudCost

import pandas as pd
import numpy as np
from predict_time_sources import feature_preparation

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
            elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
                self.__time_series_forecasting()

    def __classification(self):
        """Execute the tabular classification task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        if len(y.unique()) == 2:
            classification_type = "binary"
        else:
            classification_type =  "multiclass"
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type=classification_type,
                    objective=self.__get_metric(),
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

    def __time_series_forecasting(self):
        """Execute the tabular classification task and export the found model"""

        self.df, test = data_loader(self._configuration)
        index_column_name = self.__get_index_column() 
        index_column_copy_name = index_column_name + 'copy'
        self.df[index_column_copy_name] = self.df[index_column_name]
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        # in oder to fix this bug : 
        # bug: X.set_index(index_columns, inplace=True) => if indexcolumn is setted, evalml can not run auto ml search
        # i create a copy column for index column
        print(X)
        #problem_config = {"gap": 0, "max_delay": 7, "forecast_horizon": 7, "time_index": self.__get_index_column()}
        problem_config = {"gap": 0, "max_delay": 7, "forecast_horizon": 7, "time_index": index_column_copy_name}
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type="time series regression",
                    max_batches=1,
                    verbose=False,
                    problem_configuration=problem_config,
                    allowed_model_families=[
                        "xgboost",
                    ],
                )
        automl.search()
        best_pipeline_tobe_export = automl.best_pipeline
        #self._configuration['dataset_configuration']['TESTTTTT'] ="BABCBABC"
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')
        
        file_path = self._configuration["dataset_path"][:-4] + "timeseries\\"
        print(file_path)
        # create dir for time series test dataset
        try:
            os.mkdir(file_path)
        except:
            print("Dir already existed")
        file_path = write_tabular_dataset_test_data(test, os.path.dirname(file_path), self._configuration)
        print(file_path)

    def __get_index_column(self):
        for column, dt in self._configuration['dataset_configuration']['schema'].items():
            if dt.get("role_selected", "") == ":index":
                print(column)
                return column
        return None #
    
    def __get_metric(self):
        metrics_dict = {
            ':binary_accuracy' : "Accuracy Binary",
            ':balanced_accuracy' : "Balanced Accuracy Binary",
            ':accuracy' : "Accuracy Multiclass",
        }
        try:
            return metrics_dict[self._configuration['configuration']['parameters'][':metric']]
        except:
            print("no metric param")
        return "auto" 



