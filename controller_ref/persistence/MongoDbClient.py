import os
from pymongo import MongoClient
from pymongo.collection import Collection
from mongomock import MongoClient as MongoMockClient
from bson.objectid import ObjectId
import shutil, logging

class MongoDbClient:
    """
    MongoDB database interface API.
    ---
    Do not use independently, always use the public MongoDbStorage API.
    ---
    Everything regarding MongoDB should live in this class.
    """

    def __init__(self, server_url="mongodb://root:example@localhost"):
        self.__log = logging.getLogger('MongoDbClient')
        self.__log.setLevel(logging.getLevelName(os.getenv("PERSISTENCE_LOGGING_LEVEL")))
        if server_url is not None:
            self.__mongo = self.__use_real_database(server_url)
        else:
            self.__mongo = MongoMockClient()
        self.__log.info("New mongo db client intialized.")


    def __use_real_database(server_url: str) -> MongoClient:
        """
        Connects to a MongoDB database at the url.
        ---
        Parameter
        1. server url with host as defined in docker-compose.yml
        ---
        Returns database interface
        """
        try:
            # sample credentials from docker-compose
            # NOTE: when running this script in a container defined in docker-compose.yml,
            #       the url for MongoClient needs to match the database service name
            #       --> eg. "mongodb://root:example@mongo"
            mongo = MongoClient(server_url, 27017,
                # timeout to find a database server
                serverSelectionTimeoutMS=30000)
            
            # we want to fail as fast as possible when the database is not reachable.
            #   by default pymongo will lazy initialize and waits for the first 'real' database 
            #   interaction to connect to MongoDB
            mongo.list_databases()

            return mongo
        except:
            raise Exception("cannot find MongoDB! URL "+ server_url +"\n    Did you forget to launch it with `docker-compose up --build mongo`?")

    ####################################
    ## MISC MONGO DB OPERATIONS
    ####################################
    def drop_database(self, user_identifier: str):
        """
        Delete all datasets sessions and models for a user
        ---
        Parameter
        1. user identifier
        """
        self.__mongo.drop_database(user_identifier)
        self.__log.debug(f"drop_database: database {user_identifier} dropped")

    def check_if_user_exists(self, user_identifier: str) -> bool:
        """
        Check if user exists by checking if his database exists
        ---
        Parameter
        1. user identifier: name of the user
        ---
        Returns database existance status, TRUE == EXITS
        """
        if user_identifier in self.__mongo.list_databases() == True:
            self.__log.debug(f"check_if_user_exists: database {user_identifier} exists")
            return True
        else:
            self.__log.debug(f"check_if_user_exists: database {user_identifier} does not exists")
            return False

    ####################################
    ## DATASET MONGO DB OPERATIONS
    ####################################
    def insert_dataset(self, user_identifier: str, dataset: 'dict[str, str]') -> str:
        """
        Insert a new dataset
        ---
        Parameter
        1. user identifier
        2. dataset as dict
        ---
        Returns dataset id
        """
        datasets: Collection = self.__mongo[user_identifier]["datasets"]
        result = datasets.insert_one(dataset)
        self.__log.debug(f"insert_dataset: new dataset inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_dataset(self, user_identifier: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """
        Get a dataset by it's name
        ---
        Parameter
        1. user identifier
        2. dataset name
        ---
        Returns dataset as dict or `None`
        """
        datasets: Collection = self.__mongo[user_identifier]["datasets"]
        self.__log.debug(f"get_dataset: documents within dataset: {datasets.count_documents}")
        return datasets.find_one(filter)

    def get_datasets(self, user_identifier: str) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user
        ---
        Parameter
        1. user identifier
        2. dataset name
        ---
        Returns dataset as dict
        """
        datasets: Collection = self.__mongo[user_identifier]["datasets"]
        self.__log.debug(f"get_datasets: documents within dataset: {datasets.count_documents}")
        return datasets.find()

    def update_dataset(self, user_identifier: str, id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update a dataset record
        ---
        Parameter
        1. user identifier
        2. dataset id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        datasets: Collection = self.__mongo[user_identifier]["datasets"]
        result = datasets.update_one({ "_id": ObjectId(id) }, { "$set": new_values })
        self.__log.debug(f"update_dataset: documents changed within dataset: {result.modified_count}")
        return result.modified_count >= 1

    def delete_dataset(self, user_identifier: str, filter: 'dict[str, object]'):
        """
        Delete a dataset record and all it's associated records and files
        ---
        Parameter
        1. user identifier
        2. deletion filter
        ---
        Returns amount of deleted objects
        """
        datasets: Collection = self.__mongo[user_identifier]["datasets"]
        result = datasets.delete_one(filter)
        return result.deleted_count

    ####################################
    ## MODEL MONGO DB OPERATIONS
    ####################################
    def insert_model(self, user_identifier: str, model_details: 'dict[str, str]') -> str:
        """
        Insert model
        ---
        Parameter
        1. user identifier
        2. model as dict
        ---
        Returns model id
        """
        models: Collection = self.__mongo[user_identifier]["models"]
        result = models.insert_one(model_details)
        self.__log.debug(f"insert_model: new model inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_model(self, user_identifier: str, id: str) -> 'dict[str, object]':
        """
        Get a model by it's id
        ---
        Parameter
        1. user identifier
        2. model id
        ---
        Returns training as dict
        """
        models: Collection = self.__mongo[user_identifier]["models"]
        self.__log.debug(f"get_model: documents within model: {models.count_documents}")
        return models.find_one({ "_id": ObjectId(id) })

    def get_models(self, user_identifier: str, filter: str=None) -> 'list[dict[str, object]]':
        """
        Get all models from a user
        ---
        Parameter
        1. user identifier
        2. optional filter
        ---
        Returns models as list of dicts
        """
        models: Collection = self.__mongo[user_identifier]["models"]
        self.__log.debug(f"get_models: documents within models: {models.count_documents}")
        return models.find(filter)

    def update_model(self, user_identifier: str, id: str, new_values: 'dict[str, str]') -> bool:
        """
        Update a model record
        ---
        Parameter
        1. user identifier
        2. training id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        models: Collection = self.__mongo[user_identifier]["models"]
        result = models.update_one({ "_id": ObjectId(id) }, { "$set": new_values })
        self.__log.debug(f"update_model: documents changed within models: {result.modified_count}")
        return result.modified_count >= 1

    def delete_models(self, user_identifier: str, filter: 'dict[str, object]'):
        """
        Delete models record and all it's associated records and files
        ---
        Parameter
        1. user identifier
        2. deletion filter
        ---
        Returns amount of deleted objects
        """
        models = self.GetModels(user_identifier, filter)
        for model in list(models):
            path: str = model["path"]
            if model["automl_name"] == ":alphad3m":
                path = path.replace("\\export\\alphad3m-export.zip", "")
            elif model["automl_name"] == ":autocve":
                path = path.replace("\\export\\autocve-export.zip", "")
            elif model["automl_name"] == ":autogluon":
                path = path.replace("\\export\\gluon-export.zip", "")
            elif model["automl_name"] == ":autokeras":
                path = path.replace("\\export\\keras-export.zip", "")
            elif model["automl_name"] == ":autopytorch":
                path = path.replace("\\export\\pytorch-export.zip", "")
            elif model["automl_name"] == ":autosklearn":
                path = path.replace("\\export\\sklearn-export.zip", "")
            elif model["automl_name"] == ":flaml":
                path = path.replace("\\export\\flaml-export.zip", "")
            elif model["automl_name"] == ":mcfly":
                path = path.replace("\\export\\mcfly-export.zip", "")
            elif model["automl_name"] == ":mljar":
                path = path.replace("\\export\\mljar-export.zip", "")
            try:
                self.__log.debug(f"delete_models: deleting files within path: {path}")
                shutil.rmtree(path)
            except:
                print("path not found: " + path)
        models: Collection = self.__mongo[user_identifier]["models"]
        result = models.delete_many(filter)
        self.__log.debug(f"delete_models: documents deleted within models: {result.deleted_count}")
        return result.deleted_count

    ####################################
    ## TRAINING MONGO DB OPERATIONS
    ####################################

    def insert_training(self, user_identifier: str, training_config: 'dict[str, str]'):
        """
        Insert training
        ---
        Parameter
        1. user identifier
        2. training as dict
        ---
        Returns training id
        """
        trainings: Collection = self.__mongo[user_identifier]["trainings"]
        result = trainings.insert_one(training_config)
        self.__log.debug(f"insert_training: new training inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_training(self, user_identifier: str, id: str) -> 'dict[str, object]':
        """
        Get a training by it's id
        ---
        Parameter
        1. user_identifier
        2. training id
        ---
        Returns training as dict
        """
        trainings: Collection = self.__mongo[user_identifier]["trainings"]
        self.__log.debug(f"get_training: documents within trainings: {trainings.count_documents}")
        return trainings.find_one({ "_id": ObjectId(id) })

    def get_trainings(self, user_identifier: str) -> 'list[dict[str, object]]':
        """
        Get all trainings from a user
        ---
        Parameter
        1. user identifier
        ---
        Returns trainings as list of dicts
        """
        trainings: Collection = self.__mongo[user_identifier]["trainings"]
        self.__log.debug(f"get_trainings: documents within trainings: {trainings.count_documents}")
        return trainings.find()

    def update_training(self, user_identifier: str, id: str, new_values: 'dict[str, str]') -> bool:
        """
        Update a training record
        ---
        Parameter
        1. user identifier
        2. training id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        trainings: Collection = self.__mongo[user_identifier]["trainings"]
        result = trainings.update_one({ "_id": ObjectId(id) }, { "$set": new_values })
        self.__log.debug(f"update_training: documents changed within trainings: {result.modified_count}")
        return result.modified_count >= 1

    def delete_training(self, user_identifier: str, filter: 'dict[str, object]'):
        """
        Delete trainings record and all it's associated records and files
        ---
        Parameter
        1. user identifier
        2. deletion filter
        ---
        Returns amount of deleted objects
        """
        trainings: Collection = self.__mongo[user_identifier]["trainings"]
        result_training = trainings.find(filter)
        for training in list(result_training):
            amount_model = self.delete_models(user_identifier, { "training_id": str(training["_id"])})
            self.__log.debug(f"delete_training: documents deleted within models: {amount_model}")
        result = trainings.delete_many(filter)
        self.__log.debug(f"delete_training: documents deleted within trainings: {result.deleted_count}")
        return result.deleted_count

