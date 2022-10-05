
from enum import auto
from AdapterPredictionManager import AdapterPredictionManager
from DataStorage import DataStorage
import json, logging, os, asyncio
from ControllerBGRPC import *
from AdapterManager import AdapterManager

class AdapterRuntimePredictionManager:

    def __init__(self, data_storage: DataStorage, request: "ModelPredictRequest", prediction_identifier) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__request = request
        self.__prediction_identifier = prediction_identifier
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

        found, model = self.__data_storage.get_model(self.__request.user_identifier, self.__request.model_identifier)
        found, training = self.__data_storage.get_training(self.__request.user_identifier, model["training_identifier"])
        found, prediction_dataset = self.__data_storage.get_prediction_dataset(self.__request.user_identifier, self.__request.prediction_dataset_identifier)
        prediction_configuration = {
            "training_identifier": str(training["_id"]),
            "user_identifier": self.__request.user_identifier,
            "dataset_identifier": training["dataset_identifier"],
            "prediction_identifier": self.__prediction_identifier,
            "task": training["task"],
            "configuration": training["configuration"],
            "dataset_configuration": training["dataset_configuration"],
            "runtime_constraints": training["runtime_constraints"],
            "test_configuration": training["test_configuration"],
            "file_configuration": training["file_configuration"],
            "metric": training["metric"],
            "prediction_dataset_path": prediction_dataset["path"]
        }
        prediction_configuration["test_configuration"]["method"] = 1
        prediction_configuration["test_configuration"]["split_ratio"] = 0

        self.__log.debug("create_new_prediction: creating new blackboard and strategy controller for training")
        
        self.__log.debug(f"create_new_prediction: getting adapter endpoint information for automl {model['automl_name']}")
        host, port = map(os.getenv, self.__automl_addresses[model["automl_name"].lower()])
        port = int(port)
        self.__log.debug(f"create_new_prediction: creating new prediction adapter manager and adapter manager agent")
        adapter_prediction = AdapterPredictionManager(self.__data_storage, self.__request, prediction_configuration, self.__request.user_identifier, model['automl_name'], str(training["_id"]), host, port, self.__prediction_identifier, self.__adapter_finished_callback)
        self.__adapters.append(adapter_prediction)
        adapter_prediction.start()

    def __adapter_finished_callback(self, training_identifier, user_identifier, model_identifier, model_details: 'dict[str, object]', adapter_manager: AdapterManager):
        return        