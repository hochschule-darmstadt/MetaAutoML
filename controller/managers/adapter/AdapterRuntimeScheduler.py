from DataStorage import DataStorage
import logging, os
from ControllerBGRPC import *
from AdapterRuntimeManager import AdapterRuntimeManager
from AdapterRuntimePredictionManager import AdapterRuntimePredictionManager
from ThreadLock import ThreadLock

class AdapterRuntimeScheduler:
    """The AdapterRuntimeScheduler is a singleton object holding the running training and prediction sessions
    """

    def __init__(self, data_storage: DataStorage, explainable_lock: ThreadLock) -> None:
        """Initialize a new AdapterRuntimeScheduler instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            explainable_lock (ThreadLock): The explainable lock instance to protect from multiple thread using critical parts of the ExplainableAIManager module
        """
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('AdapterRuntimeScheduler')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__running_trainings: dict[str, AdapterRuntimeManager] = {}
        self.__running_online_predictions: dict[str, AdapterRuntimeManager] = {}
        self.__explainable_lock = explainable_lock
        return

    def create_new_training(self, request: CreateTrainingRequest, training_id: str, dataset):
        """Create a new training session and add it to the running training list

        Args:
            request (CreateTrainingRequest): The GRPC request message holding the training configuration
            training_id (str): The training id which identify the new training session
            dataset (_type_): The dataset record used by the training session
        """
        adapter_runtime_manager: AdapterRuntimeManager = AdapterRuntimeManager(self.__data_storage, request, training_id, dataset, self.__explainable_lock)
        adapter_runtime_manager.create_new_training()
        self.__running_trainings[training_id] = adapter_runtime_manager

    def create_new_prediction(self, user_id: str, prediction_id: str):
        """Create a new prediction session and add it to the running prediction list

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            prediction_id (str): The prediction id which identify the new prediction session
        """
        adapter_runtime_manager: AdapterRuntimePredictionManager = AdapterRuntimePredictionManager(self.__data_storage, user_id, prediction_id)
        self.__running_online_predictions[prediction_id] = adapter_runtime_manager
        adapter_runtime_manager.create_new_prediction()
