import os
from pymongo import MongoClient
from pymongo.collection import Collection
from mongomock import MongoClient as MongoMockClient
from bson.objectid import ObjectId
import logging
from MeasureDuration import MeasureDuration

class MongoDbClient:
    """
    MongoDB database interface API. Not to be used independently, always use the public MongoDbStorage API.
    """

    def __init__(self, server_url="mongodb://root:example@localhost"):
        """Initialize a new MongoDbClient instance.

        Args:
            server_url (str, optional): The connection URL to a MongoDB server. Defaults to "mongodb://root:example@localhost".
        """
        with MeasureDuration() as m:
            self.__log = logging.getLogger('MongoDbClient')
            self.__log.setLevel(logging.getLevelName(os.getenv("PERSISTENCE_LOGGING_LEVEL")))
            if server_url is not None:
                self.__mongo = self.__use_real_database(server_url)
            else:
                self.__mongo = MongoMockClient()
            self.__log.info("New mongo db client intialized.")


    def __use_real_database(self, server_url: str) -> MongoClient:
        """Connect to a real MongoDB server

        Args:
            server_url (str): The connection URL to a MongoDB server

        Raises:
            Exception: Raised when MongoDB could not be reached

        Returns:
            MongoClient: The MongoClient instance to interact with the connected MongoDB server
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
        """Drop a user database from MongoDB

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
        """
        self.__mongo.drop_database(user_id)
        self.__log.debug(f"drop_database: database {user_id} dropped")

    def check_if_user_exists(self, user_id: str) -> bool:
        """Check if a user database already exists

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend

        Returns:
            bool: True if the user already has a database, False if the user does not have a database
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
        """Insert a new dataset record into a users database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            dataset_details (dict[str, str]): Dictonary with the record fields and values for the new record

        Returns:
            str: The record id of the newly inserted dataset record
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"insert_dataset: inserting new dataset with values: {dataset_details}")
        result = datasets.insert_one(dataset_details)
        self.__log.debug(f"insert_dataset: new dataset inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_dataset(self, user_id: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """Retrieve a single dataset record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object]): Dictionary of record fields to filter the dataset record from

        Returns:
            dict[str, object]: Dictonary representing a dataset record
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"get_dataset: documents within dataset: {datasets.count_documents}, filter {filter}")
        return datasets.find_one(filter)

    def get_datasets(self, user_id: str, filter: 'dict[str, object]'={}) -> 'list[dict[str, object]]':
        """Retrieve all dataset records from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object], optional): Dictionary of record fields to filter the dataset records from. Defaults to {}.

        Returns:
            list[dict[str, object]]: List of dictonaries representing dataset records
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"get_datasets: documents within dataset: {datasets.count_documents}, filter {filter}")
        return datasets.find(filter)

    def update_dataset(self, user_id: str, dataset_id: str, new_values: 'dict[str, object]') -> bool:
        """Update a single dataset record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            dataset_id (str): The dataset id of the dataset record which is to be updated
            new_values (dict[str, object]): Dictonary of new dataset record field values that will be updated

        Returns:
            bool: True if the record was updated, False if the record was not updated
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]
        self.__log.debug(f"update_dataset: updating dataset with id: {dataset_id}, with new values {new_values}")
        result = datasets.update_one({ "_id": ObjectId(dataset_id) }, { "$set": new_values })
        self.__log.debug(f"update_dataset: documents changed within dataset: {result.modified_count}")
        return result.modified_count >= 1

    def delete_dataset(self, user_id: str, dataset_id: str) -> int:
        """Delete a single dataset record, by applying soft delete (setting the livecycle of the dataset record to 'deleted')

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            dataset_id (str): The dataset id of the dataset record which is to be updated

        Returns:
            int: amount of dataset deleted
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
        """Insert a new model record into a users database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model_details (dict[str, str]): Dictonary with the record fields and values for the new record

        Returns:
            str: The record id of the newly inserted model record
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"insert_model: inserting new model with values: {model_details}")
        result = models.insert_one(model_details)
        self.__log.debug(f"insert_model: new model inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_model(self, user_id: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """Retrieve a single model record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object]): Dictionary of record fields to filter the model record from

        Returns:
            dict[str, object]: Dictonary representing a model record
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"get_model: documents within model: {models.count_documents}, filter {filter}")
        return models.find_one(filter)

    def get_models(self, user_id: str, filter: 'dict[str, object]'={}) -> 'list[dict[str, object]]':
        """Retrieve all model records from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object], optional): Dictionary of record fields to filter the model records from. Defaults to {}.

        Returns:
            list[dict[str, object]]: List of dictonaries representing model records
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"get_models: documents within models: {models.count_documents}, filter {filter}")
        return models.find(filter)

    def update_model(self, user_id: str, model_id: str, new_values: 'dict[str, str]') -> bool:
        """Update a single model record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model_id (str): The model id of the model record which is to be updated
            new_values (dict[str, object]): Dictonary of new model record field values that will be updated

        Returns:
            bool: True if the record was updated, False if the record was not updated
        """
        models: Collection = self.__mongo[user_id]["models"]
        self.__log.debug(f"update_model: updating model with id: {model_id}, with new values {new_values}")
        result = models.update_one({ "_id": ObjectId(model_id) }, { "$set": new_values })
        self.__log.debug(f"update_model: documents changed within models: {result.modified_count}")
        return result.modified_count >= 1

    def delete_model(self, user_id: str, model_id: str) -> int:
        """Delete a single model record, by applying soft delete (setting the livecycle of the model record to 'deleted')

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model_id (str): The model id of the model record which is to be updated

        Returns:
            int: amount of model deleted
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

    def insert_training(self, user_id: str, training_details: 'dict[str, str]') -> str:
        """Insert a new training record into a users database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            training_details (dict[str, str]): Dictonary with the record fields and values for the new record

        Returns:
            str: The record id of the newly inserted training record
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"insert_training: inserting new training with values: {training_details}")
        result = trainings.insert_one(training_details)
        self.__log.debug(f"insert_training: new training inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_training(self, user_id: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """Retrieve a single training record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object]): Dictionary of record fields to filter the training record from

        Returns:
            dict[str, object]: Dictonary representing a training record
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"get_training: documents within trainings: {trainings.count_documents}, filter {filter}")
        return trainings.find_one(filter)

    def get_trainings(self, user_id: str, filter: 'dict[str, object]'={}) -> 'list[dict[str, object]]':
        """Retrieve all training records from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object], optional): Dictionary of record fields to filter the training records from. Defaults to {}.

        Returns:
            list[dict[str, object]]: List of dictonaries representing training records
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"get_trainings: documents within trainings: {trainings.count_documents}, filter {filter}")
        return trainings.find(filter)

    def update_training(self, user_id: str, training_id: str, new_values: 'dict[str, str]') -> bool:
        """Update a single training record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            training_id (str): The training id of the training record which is to be updated
            new_values (dict[str, object]): Dictonary of new training record field values that will be updated

        Returns:
            bool: True if the record was updated, False if the record was not updated
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        self.__log.debug(f"update_training: updating training with id: {training_id}, with new values {new_values}")
        result = trainings.update_one({ "_id": ObjectId(training_id) }, { "$set": new_values })
        self.__log.debug(f"update_training: documents changed within trainings: {result.modified_count}")
        return result.modified_count >= 1

    def delete_training(self, user_id: str, training_id: str) -> int:
        """Delete a single training record, by applying soft delete (setting the livecycle of the training record to 'deleted')

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            training_id (str): The training id of the training record which is to be updated

        Returns:
            int: amount of training deleted
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
        """Insert a new prediction record into a users database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            prediction_details (dict[str, str]): Dictonary with the record fields and values for the new record

        Returns:
            str: The record id of the newly inserted prediction record
        """
        datasets: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"insert_prediction: inserting new dataset with values: {prediction_details}")
        result = datasets.insert_one(prediction_details)
        self.__log.debug(f"insert_prediction: new dataset inserted: {result.inserted_id}")
        return str(result.inserted_id)

    def get_prediction(self, user_id: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """Retrieve a single prediction record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object]): Dictionary of record fields to filter the prediction record from

        Returns:
            dict[str, object]: Dictonary representing a prediction record
        """
        predictions: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"get_prediction: documents within dataset: {predictions.count_documents}, filter {filter}")
        return predictions.find_one(filter)

    def get_predictions(self, user_id: str, filter: 'dict[str, object]'={}) -> 'list[dict[str, object]]':
        """Retrieve all prediction records from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object], optional): Dictionary of record fields to filter the prediction records from. Defaults to {}.

        Returns:
            list[dict[str, object]]: List of dictonaries representing prediction records
        """
        predictions: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"get_predictions: documents within dataset: {predictions.count_documents}, filter {filter}")
        return predictions.find(filter)

    def update_prediction(self, user_id: str, prediction_id: str, new_values: 'dict[str, object]') -> bool:
        """Update a single prediction record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            prediction_id (str): The prediction id of the prediction record which is to be updated
            new_values (dict[str, object]): Dictonary of new prediction record field values that will be updated

        Returns:
            bool: True if the record was updated, False if the record was not updated
        """
        predictions: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"update_prediction: updating dataset with id: {prediction_id}, with new values {new_values}")
        result = predictions.update_one({ "_id": ObjectId(prediction_id) }, { "$set": new_values })
        self.__log.debug(f"update_prediction: documents changed within dataset: {result.modified_count}")
        return result.modified_count >= 1

    def delete_prediction(self, user_id: str, prediction_id: str):
        """Delete a single prediction record, by applying soft delete (setting the livecycle of the prediction record to 'deleted')

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            prediction_id (str): The prediction id of the prediction record which is to be updated

        Returns:
            int: amount of prediction deleted
        """
        predictions: Collection = self.__mongo[user_id]["predictions"]
        self.__log.debug(f"delete_prediction: setting soft delete for prediction id: {prediction_id}")
        result = predictions.update_one({ "_id": ObjectId(prediction_id) }, { "$set": { "lifecycle_state": "deleted"} })
        self.__log.debug(f"delete_prediction: soft delete for {result.matched_count} documents")
        return result.matched_count
#endregion
    
    