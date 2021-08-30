import os
import numpy as np
import pandas as pd
from supervised.automl import AutoML
from sklearn.metrics import accuracy_score

class StructuredDataAutoML(object):
    """description of class"""
    
    def __init__(self, json):
        self.__json = json
        return

    def __read_training_data(self):
		#In case of AutoKeras we only provide the training file path
        self.__target = self.__json["configuration"]["target"]
        self.__training_data_path = os.path.join(self.__json["file_location"], self.__json["file_name"])
        self.__training_data = pd.read_csv(self.__training_data_path)
        self.__training_X, self.__training_y = self.__training_data.drop([self.__target], axis=1), self.__training_data[self.__target]
        return

    def __export_model(self, model):
        #Models are automatically saved by library
        return

    def classification(self):
        self.__read_training_data()
        automl = AutoML(total_time_limit=200)
        automl.fit(self.__training_X, self.__training_y)
        self.__export_model(self.__training_X, self.__training_y)
        return

    def regression(self):
        self.__read_training_data()
        return