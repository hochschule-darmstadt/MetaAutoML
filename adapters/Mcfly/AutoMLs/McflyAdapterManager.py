from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property

class McflyAdapterManager(AdapterManager):
    def __init__(self) -> None:
        super(McflyAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "mcfly"

    def _get_ml_model_and_lib(self, config):
            # Mcfly is based on the TensorFlow/Keras library
        return (":tensorflow_lib", ":artificial_neural_network")

    def _load_model_and_make_probabilities(self, config_json, result_folder_location, dataframe):
        return