from dependency_injector import containers, providers
import os
from MongoDbClient import MongoDbClient
from JsonUtil import get_config_property
from DatasetManager import DatasetManager
from OntologyManager import OntologyManager
from TrainingManager import TrainingManager
from ModelManager import ModelManager
from UserManager import UserManager
from DataStorage import DataStorage

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class Ressources(containers.DeclarativeContainer):
    if os.getenv("MONGO_DB_DEBUG") == "YES":
        mongo_db_url = "mongodb://localhost:27017/"
    elif os.getenv("MONGO_CLUSTER") == "YES":
        mongo_db_url = "mongodb://"+os.getenv("MONGODB_SERVICE_HOST")+":"+os.getenv("MONGODB_SERVICE_PORT")+""
    else:
        mongo_db_url = "mongodb://root:example@mongo"

    data_storage_dir = os.path.join(ROOT_PATH, get_config_property("datasets-path"))

    mongo_db_client = providers.ThreadSafeSingleton(
        MongoDbClient,
        server_url=mongo_db_url
    )

    data_storage = providers.Factory(
        DataStorage,
        data_storage_dir=data_storage_dir,
        mongo_db=mongo_db_client
    )
    ontology_manager = providers.ThreadSafeSingleton(
        OntologyManager
    )

class Managers(containers.DeclarativeContainer):
    ressources = providers.DependenciesContainer()
    dataset_manager = providers.Factory(
        DatasetManager,
        data_storage=ressources.data_storage
    )
    training_manager = providers.Factory(
        TrainingManager,
        data_storage=ressources.data_storage
    )
    model_manager = providers.Factory(
        ModelManager,
        data_storage=ressources.data_storage
    )
    user_manager = providers.Factory(
        UserManager,
        data_storage=ressources.data_storage
    )

class Application(containers.DeclarativeContainer):
    ressources = providers.Container(
        Ressources,
    )
    managers =  providers.Container(
        Managers,
        ressources=ressources,
    )