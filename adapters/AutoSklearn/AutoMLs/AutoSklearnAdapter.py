import os

import autosklearn.classification
import autosklearn.regression
import pandas as pd
from AbstractAdapter import AbstractAdapter
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from JsonUtil import get_config_property
from predict_time_sources import SplitMethod


class AutoSklearnAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of AutoSklearnAdapter
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        super().__init__(configuration)

        if self._configuration["configuration"]["metric"] == "":
            # handle empty metric field, None is the default metric parameter for AutoSklearn
            self._configuration["configuration"]["metric"] = None
        self._result_path = self._configuration["model_folder_location"]
        return

    def start(self):
        """
        Execute the ML task
        """
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()

    def __generate_settings(self):
        automl_settings = {"logging_config": self.__get_logging_config()}
        if self._configuration["configuration"]["runtime_limit"] != 0:
            automl_settings.update(
                {"time_left_for_this_task": (self._configuration["configuration"]["runtime_limit"] * 60)}) #convert into seconds
        automl_settings.update({"metric": None})
        return automl_settings

    def __tabular_classification(self):
        """
        Execute the classification task
        """
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        automl_settings = self.__generate_settings()
        auto_cls = autosklearn.classification.AutoSklearnClassifier(**automl_settings)
        auto_cls.fit(X, y)

        export_model(auto_cls, self._configuration["result_folder_location"], "model_sklearn.p")

    def __tabular_regression(self):
        """
        Execute the regression task
        """
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        automl_settings = self.__generate_settings()
        auto_reg = autosklearn.regression.AutoSklearnRegressor(**automl_settings)
        auto_reg.fit(X, y, )

        export_model(auto_reg, self._configuration["result_folder_location"], "model_sklearn.p")

    def __get_logging_config(self) -> dict:
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
