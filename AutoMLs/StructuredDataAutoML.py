import os
import pandas as pd
import autosklearn.classification
import autosklearn.regression
from sklearn.preprocessing import OrdinalEncoder
import pickle
from Utils.JsonUtil import get_config_property


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
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])

        # convert all object columns to categories, because autosklearn only supports numerical,
        # bool and categorical features
        df[df.select_dtypes(['object']).columns] = df.select_dtypes(['object']) \
            .apply(lambda x: x.astype('category'))

        target = self.__configuration["tabular_configuration"]["target"]["target"]

        self.__X = df.drop(target, axis=1)
        self.__y = df[target]

        return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        output_file = os.path.join(get_config_property('output-path'), "model_sklearn.p")
        with open(output_file, "wb") as file:
            pickle.dump(model, file)

        return

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()

        auto_cls = autosklearn.classification.AutoSklearnClassifier(
            time_left_for_this_task=self.__time_limit,
            logging_config=self.get_logging_config()
        )
        auto_cls.fit(self.__X, self.__y)

        self.__export_model(auto_cls)

        return

    def regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()

        auto_reg = autosklearn.regression.AutoSklearnRegressor(
            time_left_for_this_task=self.__time_limit,
            logging_config=self.get_logging_config()
        )
        auto_reg.fit(self.__X, self.__y, )

        self.__export_model(auto_reg)

        return

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
