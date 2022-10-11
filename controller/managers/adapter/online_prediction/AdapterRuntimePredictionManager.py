
from enum import auto
from AdapterPredictionManager import AdapterPredictionManager
from DataStorage import DataStorage
import json, logging, os, asyncio
from ControllerBGRPC import *
from AdapterManager import AdapterManager

class AdapterRuntimePredictionManager:

    def __init__(self, data_storage: DataStorage, user_id: str, prediction_id: str) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__user_id = user_id
        self.__prediction_id = prediction_id
        self.__log = logging.getLogger('AdapterPredictionManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__automl_addresses = {
            ":autokeras":       ["AUTOKERAS_SERVICE_HOST", "AUTOKERAS_SERVICE_PORT"],
            ":flaml":           ["FLAML_SERVICE_HOST",     "FLAML_SERVICE_PORT"],
            ":autosklearn":     ["SKLEARN_SERVICE_HOST",   "SKLEARN_SERVICE_PORT"],
            ":autogluon":       ["AUTOGLUON_SERVICE_HOST", "AUTOGLUON_SERVICE_PORT"],
            ":autocve":         ["AUTOCVE_SERVICE_HOST",   "AUTOCVE_SERVICE_PORT"],
            ":autopytorch":     ["PYTORCH_SERVICE_HOST",   "PYTORCH_SERVICE_PORT"],
            ":mljar":           ["MLJAR_SERVICE_HOST",     "MLJAR_SERVICE_PORT"],
            ":alphad3m":        ["ALPHAD3M_SERVICE_HOST",  "ALPHAD3M_SERVICE_PORT"],
            ":mcfly":           ["MCFLY_SERVICE_HOST", "MCFLY_SERVICE_PORT"],
        }
        self.__adapters: list[AdapterManager] = []
        return
        

    def create_new_prediction(self):

        found, prediction = self.__data_storage.get_prediction(self.__user_id, self.__prediction_id)
        found, model = self.__data_storage.get_model(self.__user_id, prediction["model_id"])
        found, training = self.__data_storage.get_training(self.__user_id, model["training_id"])
        prediction_configuration = {
            "user_id": self.__user_id,
            "dataset_id": training["dataset_id"],
            "training_id": str(training["_id"]),
            "prediction_id": self.__prediction_id,
            "configuration": training["configuration"],
            "dataset_configuration": json.dumps(training["dataset_configuration"]),
            "live_dataset_path": prediction["live_dataset_path"]
        }

        self.__log.debug("create_new_prediction: creating new blackboard and strategy controller for training")
        
        self.__log.debug(f"create_new_prediction: getting adapter endpoint information for automl {model['auto_ml_solution']}")
        host, port = map(os.getenv, self.__automl_addresses[model["auto_ml_solution"].lower()])
        port = int(port)
        self.__log.debug(f"create_new_prediction: creating new prediction adapter manager and adapter manager agent")
        adapter_prediction = AdapterPredictionManager(self.__data_storage, prediction_configuration, self.__user_id,  self.__prediction_id, host, port)
        self.__adapters.append(adapter_prediction)
        adapter_prediction.start()
