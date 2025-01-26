import os
from typing import List
from pymongo import MongoClient
from pymongo.collection import Collection
from mongomock import MongoClient as MongoMockClient
from bson.objectid import ObjectId
import logging
from ControllerBGRPC import GetHomeOverviewInformationResponse
from MeasureDuration import MeasureDuration
import pymongo
from MongoDbDocuments import MongoDbDocuments

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
                self.__db_documents = MongoDbDocuments(self.__mongo)
            else:
                self.__mongo = MongoMockClient()
                self.__db_documents = MongoDbDocuments(self.__mongo)
            self.__log.info("New mongo db client initialized.")


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
    def create_database(self, user_id: str):
        """Create a new user database in MongoDB

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
        """
        self.__db_documents.setup_collections(user_id)
        self.__log.debug(f"create_database: database {user_id} created")


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

    def get_home_overview_information(self, user_id: str) -> 'GetHomeOverviewInformationResponse':
        """Get information for the home overview page of a user (# datasets, trainings, models, active trainings)

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend

        Returns:
            GetHomeOverviewInformationResponse: The GRPC response message holding the infos for the home overview
        """
        response = GetHomeOverviewInformationResponse()
        response.dataset_amount = self.__mongo[user_id]["datasets"].count_documents({"lifecycle_state": "active"})
        response.model_amount = self.__mongo[user_id]["models"].count_documents({"lifecycle_state": "active"})
        response.training_amount = self.__mongo[user_id]["trainings"].count_documents({"lifecycle_state": "active"})
        response.running_training_amount = self.__mongo[user_id]["trainings"].count_documents({"lifecycle_state": "active", "status": "busy"})
        return response

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

    def get_dataset(self, user_id: str, filter: 'dict[str, object]', extended_pipeline: List = None) -> 'dict[str, object]':
        """Retrieve a single dataset record from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object]): Dictionary of record fields to filter the dataset record from

        Returns:
            dict[str, object]: Dictonary representing a dataset record
        """
        datasets: Collection = self.__mongo[user_id]["datasets"]

        pipeline = [
            {
                '$match': filter
            }
        ]

        if extended_pipeline is not None:
            pipeline.extend(extended_pipeline)

        # self.__log.debug(f"get_dataset: documents within dataset: {datasets.count_documents}, filter {filter}")
        return datasets.aggregate(pipeline).next()

    def get_datasets(self, user_id: str, filter: 'dict[str, object]'={}, only_five_recent:bool=False, pagination:bool=False, page_number:int=1) -> 'list[dict[str, object]]':
        """Retrieve all dataset records from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object], optional): Dictionary of record fields to filter the dataset records from. Defaults to {}.

        Returns:
            list[dict[str, object]]: List of dictonaries representing dataset records
        """
        page_size = 20
        ignore_unnecessary_fields_filter = {"schema": 0, "analysis": {"duplicate_columns": 0, "duplicate_rows": 0, "irrelevant_features": 0, "missings_per_column": 0, "missings_per_row": 0, "outlier": 0}}
        offset = (page_number - 1) * page_size
        if only_five_recent == True:
            page_size = 5
        if pagination == True:
            return self.__mongo[user_id]["datasets"].find(filter, ignore_unnecessary_fields_filter).sort("analysis.creation_date", pymongo.DESCENDING).skip(offset).limit(page_size)
        else:
            if page_size != 5:
                page_size = 0
            datasets: Collection = self.__mongo[user_id]["datasets"]
            self.__log.debug(f"get_datasets: documents within dataset: {datasets.count_documents}, filter {filter}")
            return datasets.find(filter, ignore_unnecessary_fields_filter).sort("analysis.creation_date", pymongo.DESCENDING).limit(page_size)

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

    def get_models(self, user_id: str, filter: 'dict[str, object]'={}, extended_pipeline: list[dict[str, object]] = None) -> 'list[dict[str, object]]':
        """Retrieve all model records from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object], optional): Dictionary of record fields to filter the model records from. Defaults to {}.

        Returns:
            list[dict[str, object]]: List of dictonaries representing model records
        """
        models: Collection = self.__mongo[user_id]["models"]

        pipeline = [
            {
                '$match': filter
            }
        ]

        if extended_pipeline is not None:
            pipeline.extend(extended_pipeline)

        self.__log.debug(f"get_models: documents within models: {models.count_documents}, filter {filter}")
        return models.aggregate(pipeline)

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

    def get_trainings_metadata(self, user_id: str, filter: 'dict[str, object]'={}, pagination:bool=False, page_number:int=1, page_size:int=20) -> 'list[dict[str, object]]':
        """Retrieve all training records from a user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            filter (dict[str, object], optional): Dictionary of record fields to filter the training records from. Defaults to {}.
            pagination (bool): If pagination is used
            page_number (int): the pagination page to retrieve
            page_size (int): the number of records per page

        Returns:
            list[dict[str, object]]: List of dictionaries representing training records
        """

        # Aggregation pipeline
        pipeline = [
            # Stage 1: Filter documents based on provided conditions
            # This stage reduces the number of documents early in the pipeline
            {
                '$match': filter
            },
            # Stage 2: Project only needed fields and rename _id to id
            # Reduces document size early and transforms _id field
            {
                '$project': {
                    '_id': 0,  # Exclude original _id
                    'id': { '$toString': '$_id' },  # Convert _id to string and rename
                    'dataset_id': 1,
                    'task': '$configuration.task',
                    'status': 1,
                    'start_time': '$runtime_profile.start_time',
                }
            },
            # Stage 3: Join with datasets collection
            # Adds dataset information to each training document
            {
                "$lookup": {
                    "from": "datasets",
                    "let": { "dataset_id_str": "$dataset_id" },
                    "pipeline": [
                        # Sub-pipeline to filter datasets based on dataset_id
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": [
                                        { "$toString": "$_id" },
                                        "$$dataset_id_str"
                                    ]
                                }
                            }
                        },
                        # Only get the name field from datasets
                        {
                            "$project": {
                                "_id": 0,
                                "name": 1
                            }
                        }
                    ],
                    "as": "dataset"
                }
            },
            # Stage 4: Unwind the dataset array
            # Deconstructs the dataset array created by $lookup
            # Creates a separate document for each array element
            {
                '$unwind': '$dataset'
            },
            # Stage 5: Final projection to get exact shape needed
            # Removes temporary fields and finalizes structure
            {
                '$project': {
                    'id': 1,
                    'dataset_id': 1,
                    'task': 1,
                    'status': 1,
                    'start_time': 1,
                    'dataset_name': '$dataset.name'
                }
            },
            # Stage 6: Sort the results
            # Orders documents by start_time in descending order
            # -1 means descending, 1 means ascending
            {
                '$sort': {
                    'start_time': -1
                }
            }
        ]

        # Add pagination stages only if both page and page_size are provided
        if pagination and page_number is not None and page_size is not None:
            offset = (page_number - 1) * page_size
            pipeline.extend([
                {'$skip': offset},
                {'$limit': page_size}
            ])

        # Execute the query
        return self.__mongo[user_id]["trainings"].aggregate(pipeline)


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

    def get_trainings_count(self, user_id: str) -> int:
        """Get the total number of training records for a user

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend

        Returns:
            int: The total number of training records
        """
        trainings: Collection = self.__mongo[user_id]["trainings"]
        return trainings.count_documents({"lifecycle_state": "active"})

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
        pipeline = [
            {
                '$match': filter
            }
        ]
        self.__log.debug(f"get_predictions: documents within dataset: {predictions.count_documents}, filter {filter}")

        return predictions.aggregate(pipeline)

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

