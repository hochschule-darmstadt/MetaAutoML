
from enum import auto
from DataStorage import DataStorage
import json, logging, os, asyncio
from ControllerBGRPC import *
from AdapterManager import AdapterManager

class AdapterRuntimeManager:

    def __init__(self, data_storage: DataStorage) -> None:
        self.__data_storage: DataStorage = data_storage
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
        self.__log = logging.getLogger('AdapterRuntimeManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__running_trainings: dict[str, dict[str, AdapterManager]] = {}
    def start_new_training(self, request: "CreateTrainingRequest", training_id: str, dataset, callback):
        self.__running_trainings[training_id] = {}
        for automl in request.selected_auto_mls:
            self.__log.debug(f"start_new_training: getting adapter endpoint information for automl {automl}")
            host, port = map(os.getenv, self.__automl_addresses[automl.lower()])
            port = int(port)
            self.__log.debug(f"start_new_training: adapter endpoint information for automl {automl} {host}:{port}")
            adapter_training = AdapterManager(self.__data_storage, request, automl, training_id, dataset, host, port)
            asyncio.run(adapter_training.run_new_adapter_training())
            self.__running_trainings[training_id][automl] = adapter_training