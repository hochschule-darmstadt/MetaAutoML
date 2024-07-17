from DataStorage import DataStorage
import logging, os
from ControllerBGRPC import *
from StrategyController import StrategyController
from AdapterRuntimeManager import AdapterRuntimeManager
from AdapterRuntimePredictionManager import AdapterRuntimePredictionManager
from AdapterRuntimeExplainerDashboardManager import AdapterRuntimeExplainerDashboardManager
from ThreadLock import ThreadLock
import uuid
from KubernetesClient import KubernetesClient
from OntologyManager import OntologyManager

class AdapterRuntimeScheduler:
    """The AdapterRuntimeScheduler is a singleton object holding the running training and prediction sessions
    """

    def __init__(self, data_storage: DataStorage, explainable_lock: ThreadLock, kubernetes_client: KubernetesClient, ontology_client: OntologyManager) -> None:
        """Initialize a new AdapterRuntimeScheduler instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            explainable_lock (ThreadLock): The explainable lock instance to protect from multiple thread using critical parts of the ExplainableAIManager module
        """
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('AdapterRuntimeScheduler')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__running_trainings: dict[str, StrategyController] = {}
        self.__running_online_predictions: dict[str, AdapterRuntimeManager] = {}
        self.__running_explainer_dashboards: dict[str, AdapterRuntimeExplainerDashboardManager] = {}
        self.__explainable_lock = explainable_lock
        self.__kubernetes_client = kubernetes_client
        self.__ontology_client = ontology_client
        return

    def create_new_training(self, request: CreateTrainingRequest) -> str:
        """Create a new training session and add it to the running training list

        Args:
            request (CreateTrainingRequest): The GRPC request message holding the training configuration
        Returns:
            str: The training id which identify the new training session
        """
        strategy_controller = StrategyController(self.__data_storage, request, self.__explainable_lock, self.__ontology_client)
        training_id = strategy_controller.get_training_id()
        self.__running_trainings[training_id] = strategy_controller
        return training_id

    def create_new_prediction(self, user_id: str, prediction_id: str):
        """Create a new prediction session and add it to the running prediction list

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            prediction_id (str): The prediction id which identify the new prediction session
        """
        adapter_runtime_manager: AdapterRuntimePredictionManager = AdapterRuntimePredictionManager(self.__data_storage, user_id, prediction_id)
        self.__running_online_predictions[prediction_id] = adapter_runtime_manager
        adapter_runtime_manager.create_new_prediction()

    def start_new_explainer_dashboard(self, user_id, model_id):
        result = StartDashboardResponse()
        unique_id = ""
        while True:
            unique_id = str(uuid.uuid4())
            if unique_id not in self.__running_explainer_dashboards:
                break

        adapter_runtime_manager: AdapterRuntimeExplainerDashboardManager = AdapterRuntimeExplainerDashboardManager(self.__data_storage, user_id, model_id, unique_id)
        response = adapter_runtime_manager.start_explainer_dashboard(self.__kubernetes_client)
        result.url = response.url
        result.session_id = unique_id
        self.__running_explainer_dashboards[unique_id] = adapter_runtime_manager
        return result

    def stop_explainer_dashboard(self, session_id):
        result = StopDashboardResponse()
        if self.__running_explainer_dashboards.get(session_id, "") != "":
            self.__running_explainer_dashboards[session_id].stop_explainer_dashboard(self.__kubernetes_client)
            del self.__running_explainer_dashboards[session_id]
        return result
