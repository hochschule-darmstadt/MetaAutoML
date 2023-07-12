import os
import tempfile as tmp
import warnings
import re

os.environ['JOBLIB_TEMP_FOLDER'] = tmp.gettempdir()
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

import pickle

import pandas as pd
from AdapterUtils import *
from AdapterTabularUtils import *
from autoPyTorch.api.tabular_classification import TabularClassificationTask
from autoPyTorch.api.tabular_regression import TabularRegressionTask
from autoPyTorch.api.time_series_forecasting import TimeSeriesForecastingTask

from JsonUtil import get_config_property
from predict_time_sources import feature_preparation

import AutoPytorchParameterConfig as appc


class AutoPytorchAdapter:
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
        # set either a runtime limit or an iter limit, preferring runtime over iterations.

        self._configuration = configuration

    def start(self):
        """
        Execute the ML task
        """
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()
        elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
            self.__time_series_forecasting()

    def __tabular_classification(self):
        """
        Execute the classification task
        """
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), appc.task_config)


        auto_cls = TabularClassificationTask(temporary_directory=self._configuration["model_folder_location"] + "/tmp", output_directory=self._configuration["model_folder_location"] + "/output", delete_output_folder_after_terminate=False, delete_tmp_folder_after_terminate=False)
        auto_cls.search(
                X_train=X,
                y_train=y,
                **parameters,
                total_walltime_limit=self._configuration["configuration"]["runtime_limit"]*60
            )

        export_model(auto_cls, self._configuration["result_folder_location"], "model_pytorch.p")
        export_model(model, self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    def __tabular_regression(self):
        """
        Execute the regression task
        """
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)

        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), appc.task_config)

        auto_reg = TabularRegressionTask(temporary_directory=self._configuration["model_folder_location"] + "/tmp", output_directory=self._configuration["model_folder_location"] + "/output", delete_output_folder_after_terminate=False, delete_tmp_folder_after_terminate=False)
        auto_reg.search(
                X_train=X,
                y_train=y,
                **parameters,
                total_walltime_limit=self._configuration["configuration"]["runtime_limit"]*60
            )

        export_model(auto_reg, self._configuration["result_folder_location"], "model_pytorch.p")

    def __time_series_forecasting(self):
        """
        Execute the regression task
        """
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)

        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), appc.task_config)
        self._configuration["forecasting_horizon"] = parameters["n_prediction_steps"]

        train, test = data_loader(self._configuration)

        save_configuration_in_json(self._configuration)


        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)

        y_train = [y[: -self._configuration["forecasting_horizon"]]]
        y_test = [y[-self._configuration["forecasting_horizon"]:]]
        X_train = [X[: -self._configuration["forecasting_horizon"]]]
        known_future_features = list(X.columns)
        X_test = [X[-self._configuration["forecasting_horizon"]:]]

        start_times = [X.index[0]]

        auto_reg = TimeSeriesForecastingTask(temporary_directory=self._configuration["model_folder_location"] + "/tmp", output_directory=self._configuration["model_folder_location"] + "/output", delete_output_folder_after_terminate=False, delete_tmp_folder_after_terminate=False)
        auto_reg.search(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                **parameters,
                freq ='1H', #TODO we need variable or else this will crash in big dataset as they need to know the correct time frame
                start_times=start_times,
                total_walltime_limit=self._configuration["configuration"]["runtime_limit"]*60,
                known_future_features=known_future_features,
            )

        export_model(auto_reg, self._configuration["result_folder_location"], "model_pytorch.p")
