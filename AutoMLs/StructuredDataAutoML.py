import os
import pandas as pd
import pickle
import autosklearn.classification
import autosklearn.regression

from enum import Enum, unique


@unique
class DataType(Enum):
    DATATYPE_UNKNOW = 0
    DATATYPE_STRING = 1
    DATATYPE_INT = 2
    DATATYPE_FLOAT = 3
    DATATYPE_CATEGORY = 4
    DATATYPE_BOOLEAN = 5
    DATATYPE_DATETIME = 6
    DATATYPE_IGNORE = 7


class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        self.__configuration = configuration
        # set default values
        if self.__configuration.get("time_budget") == 0:
            self.__configuration["time_budget"] = 30

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])
        target = self.__configuration["tabular_configuration"]["target"]["target"]
        self.__X = df.drop(target, axis=1)
        self.__y = df[target]

    def __dataset_preparation(self):
        # Valid types for autosklearn are numerical, categorical or boolean
        for column, dt in self.__configuration["tabular_configuration"]["features"].items():
            if DataType(dt) is DataType.DATATYPE_IGNORE:
                self.__X = self.__X.drop(column, axis=1)
            elif DataType(dt) is DataType.DATATYPE_CATEGORY:
                self.__X[column] = self.__X[column].astype('category')
        # cast target to a different datatype if necessary
        self.__cast_target()

    def __cast_target(self):
        target_dt = self.__configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_CATEGORY:
            self.__y = self.__y.astype('category')

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open("templates/output/autosklearn-model.p", "wb") as file:
            pickle.dump(model, file)

    def execute_task(self):
        """
        Execute the ML task
        """
        if self.__configuration["task"] == 1:
            self.__classification()
        elif self.__configuration["task"] == 2:
            self.__regression()

    def __generate_settings(self):
        automl_settings = {"logging_config": self.get_logging_config()}
        if self.__configuration["runtime_constraints"]["runtime_limit"] != 0:
            automl_settings.update({"time_left_for_this_task": self.__configuration["runtime_constraints"]["runtime_limit"]})
        if self.__configuration["runtime_constraints"]["max_iter"] != 0:
            automl_settings.update({"max_iter": self.__configuration["runtime_constraints"]["max_iter"]})
        return automl_settings

    def __classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        self.__dataset_preparation()

        automl_settings = self.__generate_settings()
        auto_cls = autosklearn.classification.AutoSklearnClassifier(**automl_settings)
        auto_cls.fit(self.__X, self.__y)

        self.__export_model(auto_cls)

    def __regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        self.__dataset_preparation()

        automl_settings = self.__generate_settings()
        auto_reg = autosklearn.regression.AutoSklearnRegressor(**automl_settings)
        auto_reg.fit(self.__X, self.__y, )

        self.__export_model(auto_reg)

    def get_logging_config(self) -> dict:
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
