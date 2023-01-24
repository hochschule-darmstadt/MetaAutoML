import os

import autosklearn.classification
import autosklearn.regression
import pandas as pd
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from JsonUtil import get_config_property

import autosklearn.metrics



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
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30

        if self._configuration["configuration"]["metric"] == "":
            # handle empty metric field, None is the default metric parameter for AutoSklearn
            self._configuration["configuration"]["metric"] = None
        self._result_path = self._configuration["model_folder_location"]
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

        metric = None
        if ":metric" in self._configuration["configuration"]["parameters"]:
            metric_name = self._configuration["configuration"]["parameters"][":metric"]["values"][0]
            metric = AutoSklearnAdapter.__get_classification_metric_from_ontology(metric_name)
        automl_settings.update({"metric": metric})

        return automl_settings

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        # convert all object columns to categories, because autosklearn only supports numerical, bool and categorical features
        X[X.select_dtypes(['object']).columns] = X.select_dtypes(['object']) \
        .apply(lambda x: x.astype('category'))

        automl_settings = self.__generate_settings()
        auto_cls = autosklearn.classification.AutoSklearnClassifier(**automl_settings)
        auto_cls.fit(X, y)

        export_model(auto_cls, self._configuration["result_folder_location"], "model_sklearn.p")

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
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

    def __get_classification_metric_from_ontology(ontology_name: str):
        {
            ":accuracy": autosklearn.metrics.accuracy,
            ":area_under_roc_curve": autosklearn.metrics.roc_auc,
            ":balanced_accuracy": autosklearn.metrics.balanced_accuracy,
            ":f_measure": autosklearn.metrics.f1,
            ":precision": autosklearn.metrics.precision,
            ":average_precision_score": autosklearn.metrics.average_precision,
            ":recall": autosklearn.metrics.recall,
            ":log_loss": autosklearn.metrics.log_loss,
            ":r2": autosklearn.metrics.r2,
            ":mean_squared_error": autosklearn.metrics.mean_squared_error,
            ":mean_absolute_error": autosklearn.metrics.mean_absolute_error,
            ":median_absolute_error": autosklearn.metrics.median_absolute_error
        }[ontology_name]
