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


        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
            self._iter_limit = None
        elif self._configuration["configuration"]["max_iter"] > 0:
            self._time_limit = None
            self._iter_limit = self._configuration["configuration"]["max_iter"]
        else:
            self._time_limit = 30
            self._iter_limit = None

        # self._configuration["metric"] == "" and self._configuration["task"] == ":tabular_classification":
            # handle empty metric field, 'accuracy' should be the default metric parameter for AutoPytorch classification
            #self._configuration["metric"] = 'accuracy'
        #elif self._configuration["metric"] == "" and self._configuration["task"] == ":tabular_regression":
            # handle empty metric field, 'r2' should be the default metric parameter for AutoPytorch regression
            #self._configuration["metric"] = 'r2'

    def start(self):
        """
        Execute the ML task
        """
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()

    def __tabular_classification(self):
        """
        Execute the classification task
        """
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), appc.task_config)

        auto_cls = TabularClassificationTask(temporary_directory=self._configuration["model_folder_location"] + "/tmp", output_directory=self._configuration["model_folder_location"] + "/output", delete_output_folder_after_terminate=False, delete_tmp_folder_after_terminate=False)
        auto_cls.search(
                X_train=X,
                y_train=y,
                **parameters,
                total_walltime_limit=self._time_limit*60
            )

        export_model(auto_cls, self._configuration["result_folder_location"], "model_pytorch.p")

    def __tabular_regression(self):
        """
        Execute the regression task
        """
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)

        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), appc.task_config)
        auto_reg = TabularRegressionTask(temporary_directory=self._configuration["model_folder_location"] + "/tmp", output_directory=self._configuration["model_folder_location"] + "/output", delete_output_folder_after_terminate=False, delete_tmp_folder_after_terminate=False)
        auto_reg.search(
                X_train=X,
                y_train=y,
                **parameters,
                total_walltime_limit=self._time_limit*60
            )

        export_model(auto_reg, self._configuration["result_folder_location"], "model_pytorch.p")
