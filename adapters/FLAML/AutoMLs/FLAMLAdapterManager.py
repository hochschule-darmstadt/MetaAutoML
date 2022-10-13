from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property

class FLAMLAdapterManager(AdapterManager):

    def __init__(self) -> None:
        super(FLAMLAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "flaml"

    def _get_ml_model_and_lib(self, config):
        working_dir = config.result_folder_location
        # extract additional information from automl
        with open(os.path.join(working_dir, "model_flaml.p"), 'rb') as file:
            automl = dill.load(file)
            model = automl.best_estimator
            library = automl.model.estimator.__module__.split(".")[0]

        #TODO ADD CORRECT lib and model display
        library = ":lightgbm_lib"
        model = ":light_gradient_boosting_machine"
        return library, model


    def _load_model_and_make_probabilities(self, config_json, result_folder_location, dataframe):
        # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
        if self._loaded_training_id != config_json["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            with open(result_folder_location + '/model_flaml.p', 'rb') as file:
                self.__automl = dill.load(file)
            self._loaded_training_id = config_json["training_id"]
        # Get prediction probabilities and send them back.
        probabilities = json.dumps(self.__automl.predict_proba(dataframe).tolist())
        return probabilities

    