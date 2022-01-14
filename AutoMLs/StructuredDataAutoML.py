import os
import pandas as pd
import autosklearn.classification
import autosklearn.regression
import pickle
from Utils.JsonUtil import get_config_property
from predict_time_sources import feature_preparation, DataType, SplitMethod


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
        self.__time_limit = 30
        self.__configuration = configuration
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        train = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])

        # convert all object columns to categories, because autosklearn only supports numerical,
        # bool and categorical features
        train[train.select_dtypes(['object']).columns] = train.select_dtypes(['object']) \
            .apply(lambda x: x.astype('category'))

        # split training set, only use the training portion
        if SplitMethod.SPLIT_METHOD_RANDOM == self.__configuration["test_configuration"]["method"]:
            train = train.sample(random_state=self.__configuration["test_configuration"]["random_state"], frac=1)
        else:
            train = train.iloc[:int(train.shape[0] * self.__configuration["test_configuration"]["split_ratio"])]

        target = self.__configuration["tabular_configuration"]["target"]["target"]

        self.__X = train.drop(target, axis=1)
        self.__y = train[target]

        return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        output_file = os.path.join(get_config_property('output-path'), 'tmp', "model_sklearn.p")
        with open(output_file, "wb") as file:
            pickle.dump(model, file)

    def execute_task(self):
        """
        Execute the ML task
        """
        if self.__configuration["task"] == 1:
            self.__classification()
        elif self.__configuration["task"] == 2:
            self.__regression()

    def __dataset_preparation(self):
        feature_preparation(self.__X, self.__configuration["tabular_configuration"]["features"].items())
        self.__cast_target()

    def __cast_target(self):
        target_dt = self.__configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_CATEGORY:
            self.__y = self.__y.astype('category')
        elif DataType(target_dt) is DataType.DATATYPE_BOOLEAN:
            self.__y = self.__y.astype('bool')
        elif DataType(target_dt) is DataType.DATATYPE_INT:
            self.__y = self.__y.astype('int')
        elif DataType(target_dt) is DataType.DATATYPE_FLOAT:
            self.__y = self.__y.astype('float')

    def __generate_settings(self):
        automl_settings = {"logging_config": self.get_logging_config()}
        if self.__configuration["runtime_constraints"]["runtime_limit"] != 0:
            automl_settings.update(
                {"time_left_for_this_task": self.__configuration["runtime_constraints"]["runtime_limit"]})
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
