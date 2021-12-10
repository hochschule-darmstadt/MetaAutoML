import pickle
import os
import numpy as np
import pandas as pd
from supervised.automl import AutoML
from sklearn.metrics import accuracy_score

from Utils.JsonUtil import get_config_property


class StructuredDataAutoML(object):
    """description of class"""

    def __init__(self, configuration):
        self.__configuration = configuration
        if self.__configuration["runtime_constraints"]["max_iter"] == 0:
            self.__configuration["runtime_constraints"]["max_iter"] = 3

    def __read_training_data(self):
        # In case of AutoKeras we only provide the training file path
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])
        target = self.__configuration["tabular_configuration"]["target"]["target"]
        self.__X = df.drop(target, axis=1)
        self.__y = df[target]

    def __export_model(self, model):
        output_file = os.path.join(get_config_property('output-path'), "model_autokeras.p")
        with open(output_file, 'wb') as f:
            pickle.dump(model, f)
        return

    def classification(self):
        self.__read_training_data()
        automl = AutoML(total_time_limit=200)
        automl.fit(self.__X, self.__y)
        self.__export_model(automl)
        return

    def regression(self):
        self.__read_training_data()
        raise NotImplementedError()
        return
