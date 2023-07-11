import os

import autosklearn.classification
import autosklearn.regression
import pandas as pd
from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property

import AutoSklearnParameterConfig as aspc


class AutoSklearnAdapter:
    """
    Implementation of the AutoML functionality for AutoSklearnAdapter
    """

    def __init__(self, configuration: dict):
        """Init a new instance of AutoSklearnAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        return

    def start(self):
        """Start the correct ML task functionality of AutoSklearn"""
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()

    def __generate_settings(self) -> dict:
        """Generate the autosklearn settings dictionary for the new training

        Returns:
            dict: Autosklearn setttings dictionary
        """
        automl_settings = {"logging_config": self.__get_logging_config()}
        if self._configuration["configuration"]["runtime_limit"] != 0:
            automl_settings.update(
                {"time_left_for_this_task": (self._configuration["configuration"]["runtime_limit"] * 60)}) #convert into seconds

        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), aspc.parameters)
        automl_settings.update(parameters)

        return automl_settings

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)

        automl_settings = self.__generate_settings()
        auto_cls = autosklearn.classification.AutoSklearnClassifier(**automl_settings)
        auto_cls.fit(X, y)

        export_model(auto_cls, self._configuration["result_folder_location"], "model_sklearn.p")

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        # convert all object columns to categories, because autosklearn only supports numerical, bool and categorical features
        X[X.select_dtypes(['object']).columns] = X.select_dtypes(['object']) \
        .apply(lambda x: x.astype('category'))

        automl_settings = self.__generate_settings()
        auto_reg = autosklearn.regression.AutoSklearnRegressor(**automl_settings)
        auto_reg.fit(X, y)

        export_model(auto_reg, self._configuration["result_folder_location"], "model_sklearn.p")

    def __get_logging_config(self) -> dict:
        """Generate the logging configuration dict for autosklearn

        Returns:
            dict: logging configuration dict
        """
        return {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'custom': {
                    # More format options are available in the official
                    # `documentation <https://docs.python.org/3/howto/logging-cookbook.html>`_
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },

            # Any INFO level msg will be printed to the console
            'handlers': {
                'console': {
                    'level': 'INFO',
                    'formatter': 'custom',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                },
            },

            'loggers': {
                '': {  # root logger
                    'level': 'DEBUG',
                },
                'Client-EnsembleBuilder': {
                    'level': 'DEBUG',
                    'handlers': ['console'],
                },
            },
        }
