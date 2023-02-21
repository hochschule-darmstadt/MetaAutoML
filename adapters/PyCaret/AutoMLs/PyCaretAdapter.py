import os

from AdapterUtils import *
from AdapterTabularUtils import 
import numpy as np
from sklearn.impute import SimpleImputer
import pandas as pd
import json
from JsonUtil import get_config_property
import PyCaretParameterConfig as ppc

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
        from pycaret.classification import *

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X[y.name] = y
        #TODO If index is set, index is somehow removed within pycaret and added as empty dataframe which crashes
        
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), ppc.task_config)
        automl = setup(data = X, target = y.name)
        best = compare_models(budget_time=self._configuration["configuration"]["runtime_limit"] * 60)
        dt = create_model(best)
        tuned_dt = tune_model(dt, **parameters)
        final_dt = finalize_model(tuned_dt)
        save_model(final_dt, os.path.join(self._configuration["result_folder_location"], 'model_pycaret'))

        #export_model(automl, self._configuration["result_folder_location"], 'model_pycaret.p')

    def __tabular_regression(self):
        #most likely not working, looks like a copy of the flaml adapter
        """Execute the tabular regression task and export the found model"""
        from pycaret.regression import *
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X[y.name] = y
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), ppc.task_config)
        automl = setup(data = X, target = y.name)
        best = compare_models(budget_time=self._configuration["configuration"]["runtime_limit"] * 60)
        dt = create_model(best)
        tuned_dt = tune_model(dt, **parameters)
        final_dt = finalize_model(tuned_dt)
        save_model(final_dt, os.path.join(self._configuration["result_folder_location"], 'model_pycaret'))



    def __time_series_forecasting(self):
        #most likely not working, looks like a copy of the flaml adapter
        """Execute the tabular classification task and export the found model"""
        from pycaret.time_series import *
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X[y.name] = y
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), ppc.task_config)
        automl = time_series.setup(data = X, target = y.name)
        best = time_series.compare_models()
        dt = time_series.create_model(best)
        tuned_dt = time_series.tune_model(dt, **parameters)
        final_dt = time_series.finalize_model(tuned_dt)
        time_series.save_model(final_dt, os.path.join(self._configuration["result_folder_location"], 'model_pycaret'))
        #export_model(automl, self._configuration["result_folder_location"], 'model_pycaret.p')
