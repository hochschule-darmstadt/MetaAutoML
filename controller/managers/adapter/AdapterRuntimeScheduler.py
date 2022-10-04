from DataStorage import DataStorage
import logging, os
from ControllerBGRPC import *
from AdapterRuntimeManager import AdapterRuntimeManager
from AdapterRuntimePredictionManager import AdapterRuntimePredictionManager

class AdapterRuntimeScheduler:

    def __init__(self, data_storage: DataStorage) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('AdapterRuntimeScheduler')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__running_trainings: dict[str, AdapterRuntimeManager] = {}
        self.__running_online_predictions: dict[str, AdapterRuntimeManager] = {}
        return

    def create_new_training(self, request: "CreateTrainingRequest", training_identifier: str, dataset):
        adapter_runtime_manager: AdapterRuntimeManager = AdapterRuntimeManager(self.__data_storage, request, training_identifier, dataset)
        adapter_runtime_manager.create_new_training()
        self.__running_trainings[training_identifier] = adapter_runtime_manager
        
    def create_new_prediction(self, request: "ModelPredictRequest", prediction_identifier: str):
        adapter_runtime_manager: AdapterRuntimePredictionManager = AdapterRuntimePredictionManager(self.__data_storage, request, prediction_identifier)
        self.__running_online_predictions[prediction_identifier] = adapter_runtime_manager
        adapter_runtime_manager.create_new_prediction()
