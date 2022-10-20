import os
from pymongo import MongoClient
from pymongo.collection import Collection
from mongomock import MongoClient as MongoMockClient
from bson.objectid import ObjectId
import logging
from MeasureDuration import MeasureDuration

class MongoDbClient:
    """
    MongoDB database interface API.
    ---
    Do not use independently, always use the public MongoDbStorage API.
    ---
    Everything regarding MongoDB should live in this class.
    """

    def __init__(self, server_url="mongodb://root:example@localhost"):
        with MeasureDuration() as m:
            self.__log = logging.getLogger('MongoDbClient')
            self.__log.setLevel(logging.getLevelName(os.getenv("PERSISTENCE_LOGGING_LEVEL")))
            if server_url is not None:
                self.__mongo = self.__use_real_database(server_url)
            else:
                self.__mongo = MongoMockClient()
            self.__log.info("New mongo db client intialized.")


    def __use_real_database(self, server_url: str) -> MongoClient:
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
#region
    def drop_database(self, user_id: str):
        """
        Delete all datasets sessions and models for a user
        ---
        Parameter
        1. user id
        """
        self.__mongo.drop_database(user_id)
        self.__log.debug(f"drop_database: database {user_id} dropped")

    def check_if_user_exists(self, user_id: str) -> bool:
        """
        Check if user exists by checking if his database exists
        ---
        Parameter
        1. user id: name of the user
        ---
        Returns database existance status, TRUE == EXITS
        """
        if user_id in self.__mongo.list_databases() == True:
            self.__log.debug(f"check_if_user_exists: database {user_id} exists")
            return True
        else:
            self.__log.debug(f"check_if_user_exists: database {user_id} does not exists")
            return False
#endregion
    ####################################
    ## DATASET MONGO DB OPERATIONS
    ####################################
#region
    def insert_dataset(self, user_id: str, dataset_details: 'dict[str, str]') -> str:
        """
        Insert a new dataset
        ---
        Parameter
        1. user id
        2. dataset as dict
        ---
        Returns dataset id
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"insert_dataset: inserting new dataset with values: {dataset_details}")
        result = datasets.insert_one(dataset_details)
        self.__log.debug(f"insert_dataset: new dataset inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_dataset(self, user_id: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """
        Get a dataset by filter
        ---
        Parameter
        1. user id
        2. filter dictonary to find dataset for
        ---
        Returns dataset as dict or `None`
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"get_dataset: documents within dataset: {datasets.count_documents}, filter {filter}")
        return datasets.find_one(filter)

    def get_datasets(self, user_id: str, filter: 'dict[str, object]'={}) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user, optinally by filter
        ---
        Parameter
        1. user id
        2. optional filter
        ---
        Returns dataset as dict
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"get_datasets: documents within dataset: {datasets.count_documents}, filter {filter}")
        return datasets.find(filter)

    def update_dataset(self, user_id: str, dataset_id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update a dataset record
        ---
        Parameter
        1. user id
        2. dataset id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"update_dataset: updating dataset with id: {dataset_id}, with new values {new_values}")
        result = datasets.update_one({ "_id": ObjectId(dataset_id) }, { "$set": new_values })
        self.__log.debug(f"update_dataset: documents changed within dataset: {result.modified_count}")
        return result.modified_count >= 1

    def delete_dataset(self, user_id: str, dataset_id: str):
        """
        Delete a dataset record and all it's associated records and files
        ---
        Parameter
        1. user id
        2. deletion filter
        ---
        Returns amount of deleted objects
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"delete_dataset: setting soft delete for dataset with filter: {filter}")
        result = datasets.update_one({ "_id": ObjectId(dataset_id) }, { "$set": { "lifecycle_state": "deleted"} })
        self.__log.debug(f"delete_dataset: soft delete for {result.matched_count} documents")
        return result.matched_count
#endregion
    
    ####################################
    ## MODEL MONGO DB OPERATIONS
    ####################################
#region
    def insert_model(self, user_id: str, model_details: 'dict[str, str]') -> str:
        """
        Insert model
        ---
        Parameter
        1. user id
        2. model as dict
        ---
        Returns model id
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"insert_model: inserting new model with values: {model_details}")
        result = models.insert_one(model_details)
        self.__log.debug(f"insert_model: new model inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_model(self, user_id: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """
        Get a model by it's filter
        ---
        Parameter
        1. user id
        2. filter dictonary to find model for
        ---
        Returns training as dict
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"get_model: documents within model: {models.count_documents}, filter {filter}")
        return models.find_one(filter)

    def get_models(self, user_id: str, filter: 'dict[str, object]'={}) -> 'list[dict[str, object]]':
        """
        Get all models from a user, by optionally filter
        ---
        Parameter
        1. user id
        2. optional filter
        ---
        Returns models as list of dicts
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"get_models: documents within models: {models.count_documents}, filter {filter}")
        return models.find(filter)

    def update_model(self, user_id: str, model_id: str, new_values: 'dict[str, str]') -> bool:
        """
        Update a model record
        ---
        Parameter
        1. user id
        2. training id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"update_model: updating model with id: {model_id}, with new values {new_values}")
        result = models.update_one({ "_id": ObjectId(model_id) }, { "$set": new_values })
        self.__log.debug(f"update_model: documents changed within models: {result.modified_count}")
        return result.modified_count >= 1

    def delete_model(self, user_id: str, model_id: str):
        """
        Delete model record and all it's associated records and files
        ---
        Parameter
        1. user id
        2. deletion filter
        ---
        Returns amount of deleted objects
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"delete_models: setting soft delete for model id: {model_id}")
        result = models.update_one({ "_id": ObjectId(model_id) }, { "$set": { "lifecycle_state": "deleted"} })
        self.__log.debug(f"delete_models: soft delete for {result.matched_count} documents")
        return result.matched_count
#endregion

    ####################################
    ## TRAINING MONGO DB OPERATIONS
    ####################################
#region

    def insert_training(self, user_id: str, training_details: 'dict[str, str]'):
        """
        Insert training
        ---
        Parameter
        1. user id
        2. training as dict
        ---
        Returns training id
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"insert_training: inserting new training with values: {training_details}")
        result = trainings.insert_one(training_details)
        self.__log.debug(f"insert_training: new training inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_training(self, user_id: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """
        Get a training by it's filter
        ---
        Parameter
        1. user id
        2. filter dictonary to find training for
        ---
        Returns training as dict
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"get_training: documents within trainings: {trainings.count_documents}, filter {filter}")
        return trainings.find_one(filter)

    def get_trainings(self, user_id: str, filter: 'dict[str, object]'={}) -> 'list[dict[str, object]]':
        """
        Get all trainings from a user, optionally by filter
        ---
        Parameter
        1. user id
        2. optional filter
        ---
        Returns trainings as list of dicts
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"get_trainings: documents within trainings: {trainings.count_documents}, filter {filter}")
        return trainings.find(filter)

    def update_training(self, user_id: str, training_id: str, new_values: 'dict[str, str]') -> bool:
        """
        Update a training record
        ---
        Parameter
        1. user id
        2. training id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"update_training: updating training with id: {training_id}, with new values {new_values}")
        result = trainings.update_one({ "_id": ObjectId(training_id) }, { "$set": new_values })
        self.__log.debug(f"update_training: documents changed within trainings: {result.modified_count}")
        return result.modified_count >= 1

    def delete_training(self, user_id: str, training_id: str):
        """
        Delete trainings record and all it's associated records and files
        ---
        Parameter
        1. user id
        2. deletion filter
        ---
        Returns amount of deleted objects
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"delete_training: setting soft delete for training id: {training_id}")
        result = trainings.update_one({ "_id": ObjectId(training_id) }, { "$set": { "lifecycle_state": "deleted"} })
        self.__log.debug(f"delete_training: soft delete for {result.matched_count} documents")
        return result.matched_count

#endregion
    ####################################
    ## PREDICTION DATASET MONGO DB OPERATIONS
    ####################################
#region
    def insert_prediction(self, user_id: str, prediction_details: 'dict[str, str]') -> str:
        """
        Insert a new dataset
        ---
        Parameter
        1. user id
        2. dataset as dict
        ---
        Returns dataset id
        """
        datasets: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"insert_prediction: inserting new dataset with values: {prediction_details}")
        result = datasets.insert_one(prediction_details)
        self.__log.debug(f"insert_prediction: new dataset inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_prediction(self, user_id: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """
        Get a dataset by filter
        ---
        Parameter
        1. user id
        2. filter dictonary to find dataset for
        ---
        Returns dataset as dict or `None`
        """
        predictions: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"get_prediction: documents within dataset: {predictions.count_documents}, filter {filter}")
        return predictions.find_one(filter)

    def get_predictions(self, user_id: str, filter: 'dict[str, object]'={}) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user, optinally by filter
        ---
        Parameter
        1. user id
        2. optional filter
        ---
        Returns dataset as dict
        """
        predictions: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"get_predictions: documents within dataset: {predictions.count_documents}, filter {filter}")
        return predictions.find(filter)

    def update_prediction(self, user_id: str, prediction_id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update a dataset record
        ---
        Parameter
        1. user id
        2. dataset id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        predictions: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"update_prediction: updating dataset with id: {prediction_id}, with new values {new_values}")
        result = predictions.update_one({ "_id": ObjectId(prediction_id) }, { "$set": new_values })
        self.__log.debug(f"update_prediction: documents changed within dataset: {result.modified_count}")
        return result.modified_count >= 1

    def delete_prediction(self, user_id: str, prediction_id: str):
        """
        Delete a dataset record and all it's associated records and files
        ---
        Parameter
        1. user id
        2. deletion filter
        ---
        Returns amount of deleted objects
        """
        predictions: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"delete_prediction: setting soft delete for prediction id: {prediction_id}")
        result = predictions.update_one({ "_id": ObjectId(prediction_id) }, { "$set": { "lifecycle_state": "deleted"} })
        self.__log.debug(f"delete_prediction: soft delete for {result.matched_count} documents")
        return result.matched_count
#endregion
    
    