from DataStorage import DataStorage
import logging, os
from ControllerBGRPC import *
from AdapterRuntimeManager import AdapterRuntimeManager
from AdapterRuntimePredictionManager import AdapterRuntimePredictionManager
from ThreadLock import ThreadLock

class AdapterRuntimeScheduler:

    def __init__(self, data_storage: DataStorage, explainable_lock: ThreadLock) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('AdapterRuntimeScheduler')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__running_trainings: dict[str, AdapterRuntimeManager] = {}
        self.__running_online_predictions: dict[str, AdapterRuntimeManager] = {}
        self.__explainable_lock = explainable_lock
        return

    def create_new_training(self, request: "CreateTrainingRequest", training_id: str, dataset):
        adapter_runtime_manager: AdapterRuntimeManager = AdapterRuntimeManager(self.__data_storage, request, training_id, dataset, self.__explainable_lock)
        adapter_runtime_manager.create_new_training()
        self.__running_trainings[training_id] = adapter_runtime_manager
        
    def create_new_prediction(self, user_id: str, prediction_id: str):
        adapter_runtime_manager: AdapterRuntimePredictionManager = AdapterRuntimePredictionManager(self.__data_storage, user_id, prediction_id)
        self.__running_online_predictions[prediction_id] = adapter_runtime_manager
        adapter_runtime_manager.create_new_prediction()
