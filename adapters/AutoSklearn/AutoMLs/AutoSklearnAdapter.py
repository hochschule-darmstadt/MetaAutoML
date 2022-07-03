import os
import pandas as pd
import autosklearn.classification
import autosklearn.regression
from predict_time_sources import SplitMethod
from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data, prepare_tabular_dataset, export_model

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

        if self._configuration["metric"] == "":
            # handle empty metric field, None is the default metric parameter for AutoSklearn
            self._configuration["metric"] = None
        return

    def start(self):
        """
        Execute the ML task
        """
        if self._configuration["task"] == 1:
            self.__tabular_classification()
        elif self._configuration["task"] == 2:
            self.__tabular_regression()

    def __generate_settings(self):
        automl_settings = {"logging_config": self.__get_logging_config()}
        if self._configuration["runtime_constraints"]["runtime_limit"] != 0:
            automl_settings.update(
                {"time_left_for_this_task": self._configuration["runtime_constraints"]["runtime_limit"]})
        automl_settings.update({"metric": self._configuration["metric"]})
        return automl_settings

    def __tabular_classification(self):
        """
        Execute the classification task
        """
        self.df = read_tabular_dataset_training_data(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        automl_settings = self.__generate_settings()
        auto_cls = autosklearn.classification.AutoSklearnClassifier(**automl_settings)
        auto_cls.fit(X, y)

        export_model(auto_cls, "model_sklearn.p")

    def __tabular_regression(self):
        """
        Execute the regression task
        """
        self.df = read_tabular_dataset_training_data(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        automl_settings = self.__generate_settings()
        auto_reg = autosklearn.regression.AutoSklearnRegressor(**automl_settings)
        auto_reg.fit(X, y, )

        export_model(auto_reg, "model_sklearn.p")

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
