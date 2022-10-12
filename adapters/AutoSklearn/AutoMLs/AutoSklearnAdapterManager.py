from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property

class AutoSklearnAdapterManager(AdapterManager):

    def __init__(self) -> None:
        super(AutoSklearnAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None

    def _get_ml_model_and_lib(self, config):
        # AutoSklearn uses an ensemble of up to 50 different models we are not able to show them all in our current GUI
        # autosklearn always uses only sklearn
        return ":scikit_learn_lib", ":ensemble"

    def _load_model_and_make_probabilities(self, config_json, result_folder_location, dataframe):
        # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
        if self._loaded_training_id != config_json["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            with open(result_folder_location + '/model_sklearn.p', 'rb') as file:
                    self._automl = pickle.load(file)
            self._loaded_training_id = config_json["training_id"]
            # Get prediction probabilities and send them back.
            probabilities = json.dumps(self._automl.predict_proba(dataframe).tolist())
        return probabilities

