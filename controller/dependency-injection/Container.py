import threading
from dependency_injector import containers, providers
import os, sys
from MongoDbClient import MongoDbClient
from JsonUtil import get_config_property
from DatasetManager import DatasetManager
from OntologyManager import OntologyManager
from TrainingManager import TrainingManager
from ModelManager import ModelManager
from PredictionManager import PredictionManager
from UserManager import UserManager
from DataStorage import DataStorage
from AdapterRuntimeScheduler import AdapterRuntimeScheduler
from ThreadLock import ThreadLock
from KubernetesClient import KubernetesClient
from ChatbotManager import ChatbotManager
from ChatbotServiceManager import ChatbotServiceManager

class Ressources(containers.DeclarativeContainer):
    if os.getenv("MONGO_DB_DEBUG") == "YES":
        mongo_db_url = "mongodb://localhost:27017/"
    elif os.getenv("MONGO_DB_DOCKER_DEBUG") == "YES":
        mongo_db_url = f"mongodb://root:example@{os.getenv('DEFAULT_GATEWAY_IP')}:27017/"
    elif os.getenv("MONGO_CLUSTER") == "YES":
        mongo_db_url = "mongodb://"+os.getenv("MONGODB_SERVICE_HOST")+":"+os.getenv("MONGODB_SERVICE_PORT")+""
    else:
        mongo_db_url = "mongodb://root:example@mongo"

    data_storage_dir = os.path.join(os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)), get_config_property("datasets-path"))

    mongo_db_client = providers.ThreadSafeSingleton(
        MongoDbClient,
        server_url=mongo_db_url
    )

    dataset_analysis_lock = providers.ThreadSafeSingleton(
        ThreadLock
    )

    data_storage = providers.Factory(
        DataStorage,
        data_storage_dir=data_storage_dir,
        mongo_db=mongo_db_client
    )
    ontology_manager = providers.ThreadSafeSingleton(
        OntologyManager
    )

    explainable_lock = providers.ThreadSafeSingleton(
        ThreadLock
    )

    kubernetes_client = providers.ThreadSafeSingleton(
        KubernetesClient
    )

class Managers(containers.DeclarativeContainer):
    ressources = providers.DependenciesContainer()
    adapter_runtime_scheduler = providers.ThreadSafeSingleton(
        AdapterRuntimeScheduler,
        data_storage=ressources.data_storage,
        explainable_lock=ressources.explainable_lock,
        kubernetes_client=ressources.kubernetes_client,
        ontology_client=ressources.ontology_manager
    )
    dataset_manager = providers.Factory(
        DatasetManager,
        data_storage=ressources.data_storage,
        dataset_analysis_lock=ressources.dataset_analysis_lock
    )
    training_manager = providers.Factory(
        TrainingManager,
        data_storage=ressources.data_storage,
        adapter_runtime_scheduler=adapter_runtime_scheduler
    )
    model_manager = providers.Factory(
        ModelManager,
        data_storage=ressources.data_storage,
        adapter_runtime_scheduler=adapter_runtime_scheduler
    )
    user_manager = providers.Factory(
        UserManager,
        data_storage=ressources.data_storage,
        dataset_analysis_lock=ressources.dataset_analysis_lock
    )
    prediction_manager = providers.Factory(
        PredictionManager,
        data_storage=ressources.data_storage,
        adapter_runtime_scheduler=adapter_runtime_scheduler
    )
    chatbot_manager = providers.Factory(
        ChatbotManager,

    )
    chatbot_service_manager = providers.Factory(
    ChatbotServiceManager,
    )

class Application(containers.DeclarativeContainer):


    ressources = providers.Container(
        Ressources,
    )
    managers =  providers.Container(
        Managers,
        ressources=ressources,
    )
