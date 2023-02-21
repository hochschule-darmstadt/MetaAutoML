import os
from AdapterUtils import *
from AdapterTabularUtils import *
from flaml import AutoML
import numpy as np
from sklearn.impute import SimpleImputer
import pandas as pd
import json
from JsonUtil import get_config_property
import FLAMLParameterConfig as fpc

class FLAMLAdapter:
    """
    Implementation of the AutoML functionality for FLAML
    """

    def __init__(self, configuration: dict):
        """Init a new instance of FLAMLAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30
        self._result_path = configuration["model_folder_location"]
        self._log_file_path = os.path.join(self._result_path, "flaml.log")

    def start(self):
        """Start the correct ML task functionality of FLAML"""
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()
        elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
            self.__time_series_forecasting()
        elif self._configuration["configuration"]["task"] == ":text_classification":
            self.__text_classification()

    def __generate_settings(self) -> dict:
        """Generate the settings dictionary for FLAML

        Returns:
            dict: Settings configuration for FLAML
        """
        automl_settings = {"log_file_name": 'flaml.log'}
        automl_settings.update({"time_budget": self._configuration["configuration"]["runtime_limit"] * 60})

        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), fpc.task_config)
        automl_settings.update(parameters)
        return automl_settings

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X, y = replace_forbidden_json_utf8_characters(X, y)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "task": 'classification',
            "ensemble": True,
            "log_file_name": self._log_file_path
        })

        X[y.name] = y.values
        automl.fit(dataframe=X, label=y.name, **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X, y = replace_forbidden_json_utf8_characters(X, y)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "task": 'regression',
            "ensemble": True,
            "log_file_name": self._log_file_path
        })

        X[y.name] = y.values
        automl.fit(dataframe=X, label=y.name, **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')


    def __time_series_forecasting(self):
        """Execute the tabular classification task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Reset any index and imputation
        self._configuration = reset_index_role(self._configuration)
        X.reset_index(inplace = True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        #TODO ensure ts first column is datetime
        #TODO add dynamic periode
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "task": 'ts_forecast',
            "ensemble": True,
            "log_file_name": self._log_file_path,
            "period": 12,
            "eval_method": "holdout"
        })
        #X.reset_index(inplace=True)
        #X = X.bfill().ffill()  # makes sure there are no missing values
        automl.fit(X_train=X, y_train=y, **automl_settings)

        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')

    def __text_classification(self):
        """Execute the tabular classification task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Reset any index and imputation
        self._configuration = set_column_with_largest_amout_of_text(X, self._configuration)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        X, y = replace_forbidden_json_utf8_characters(X, y)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "task": 'seq-classification',
            "ensemble": True,
            "fit_kwargs_by_estimator": {
                "transformer": {
                    "output_dir": self._configuration["model_folder_location"],   # setting the output directory
                }
            },
            "log_file_name": self._log_file_path,
            "fp16": False
        })

        X[y.name] = y.values
        automl.fit(dataframe=X, label=y.name, **automl_settings)

        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')
