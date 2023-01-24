import os

from AdapterUtils import export_model, prepare_tabular_dataset, data_loader, get_column_with_largest_amout_of_text
from pycaret.classification import *
import numpy as np
from sklearn.impute import SimpleImputer
import pandas as pd
import json
from JsonUtil import get_config_property

class PyCaretAdapter:
    """
    Implementation of the AutoML functionality for PyCaret
    """

    def __init__(self, configuration: dict):
        """Init a new instance of PyCaretAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30
        self._result_path = configuration["model_folder_location"]
        self._log_file_path = os.path.join(self._result_path, "PyCaret.log")

    def start(self):
        """Start the correct ML task functionality of PyCaret"""
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()
        elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
            self.__time_series_forecasting()

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X[y.name] = y
        automl = setup(data = X, target = y.name)
        best = compare_models()
        dt = create_model(best)
        tuned_dt = tune_model(dt)
        final_dt = finalize_model(tuned_dt)
        save_model(final_dt, os.path.join(self._configuration["result_folder_location"], 'model_pycaret'))
        #export_model(automl, self._configuration["result_folder_location"], 'model_pycaret.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            #"metric": self._configuration["configuration"]["metric"] if self._configuration["configuration"]["metric"] != "" else 'accuracy',
            "metric": 'mse',
            "task": 'regression',
            "log_file_name": self._log_file_path
        })

        X[y.name] = y.values
        automl.fit(dataframe=X, label=y.name, **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_pycaret.p')


    def __time_series_forecasting(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        #TODO ensure ts first column is datetime
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            #"metric": self._configuration["configuration"]["metric"] if self._configuration["configuration"]["metric"] != "" else 'accuracy',
            "metric": 'mape',
            "task": 'ts_forecast',
            "log_file_name": self._log_file_path,
            "period": 1,
            "eval_method": "holdout"
        })
        X[y.name] = y.values
        X.reset_index(inplace=True)
        X = X.bfill().ffill()  # makes sure there are no missing values
        automl.fit(dataframe=X, label=y.name, **automl_settings)

        export_model(automl, self._configuration["result_folder_location"], 'model_pycaret.p')
