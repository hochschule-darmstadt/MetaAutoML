import os
import pandas as pd
import pickle
from flaml import AutoML

class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """
    def __init__(self, json: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        self.__json = json
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        df = pd.read_csv(os.path.join(self.__json["file_location"], self.__json["file_name"]))
        self.__X = df.drop(self.__json["configuration"]["target"], axis=1)
        self.__y = df[self.__json["configuration"]["target"]]
        return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open('templates/output/flaml-model', 'wb') as file:
            pickle.dump(model, file)
        return

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        automl = AutoML()
        automl_settings = {
            "time_budget": 10,
            "metric": 'accuracy',
            "task": 'classification',
            "log_file_name": 'flaml.log',
        }

        automl.fit(X_train=self.__X, y_train=self.__y, **automl_settings)
        self.__export_model(automl)
        return

    def regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        automl = AutoML()
        automl_settings = {
            "time_budget": 10,
            "metric": 'rmse',
            "task": 'regression',
            "log_file_name": 'flaml.log',
        }

        automl.fit(X_train=self.__X, y_train=self.__y, **automl_settings)
        self.__export_model(automl)
        return