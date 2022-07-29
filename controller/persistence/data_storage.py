import sys
import io
import shutil
from threading import Lock
import os
import os.path
from persistence.mongo_client import Database
from bson.objectid import ObjectId
from DataSetAnalysisManager import DataSetAnalysisManager
import pandas as pd

class DataStorage:
    """
    Centralized Access to File System and Database
    """


    def __init__(self, data_storage_dir: str, database = None):
        """
        Initialize new instance. This should be done already.
        Do _not_ use multiple instances of this class.

        Will connect to the MongoDB database defined in docker-compose
        unless `database` is provided.

        >>> data_storage = DataStorage("/tmp/")

        ----
        Parameter
        1. storage directory on disk
        2. optional Database object (used for Testing)
        """
        # ensure folder exists
        os.makedirs(data_storage_dir, exist_ok=True)

        self.__storage_dir = data_storage_dir

        if database is None:
            # assume that we run with docker-compose
            self.__mongo: Database = Database("mongodb://root:example@mongo")
        else:
            self.__mongo: Database = Database(database)

        self.__lock = Lock()


    def Lock(self):
        """
        Lock access to the data storage to a single thread.
        ---
        >>> with data_store.lock():
                # critical region
                sess = data_storage.get_session(...)
                data_storage.update_session(..., {
                    "models": sess["models"] + [new_model]
                })
        """
        return DataStorage.__DbLock(self.__lock)

    def CheckIfUserExists(self, username: bool):
        """
        Check if user exists by checking if his database exists
        ---
        >>> id: str = ds.CheckIfUserExists("automl_user")
        ---
        Parameter
        1. username: name of the user
        ---
        Returns database existance status, TRUE == EXITS
        """
        return self.__mongo.CheckIfUserExists(username)

    def InsertTraining(self, username: str, training: 'dict[str, object]') -> str:
        """
        Insert single training into the database.
        ---
        >>> id: str = ds.InsertTraining("automl_user", {
                "dataset": ...,
                ...
            })

        ---
        Parameter
        1. username: name of the user
        2. training: training dict to be inserted
        ---
        Returns training id
        """
        return self.__mongo.InsertTraining(username, training)


    def GetTraining(self, username: str, id: str) -> 'dict[str, object]':
        """
        Get single training by id. 
        ---
        >>> sess = data_storage.GetTraining("automl_user", sess_id)
        >>> if sess is None:
                raise Exception("cannot find training")
        
        ---
        Parameter
        1. username: name of the user
        2. id: id of training
        ---
        Returns training as `dict` or `None` if not found.
        """
        return self.__mongo.GetTraining(username, id)

    def GetTrainings(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all trainings for a user. 
        ---
        >>> for sess in data_storage.GetTrainings("automl_user"):
                print(sess["dataset"])

        ---
        Parameter
        1. username: name of the user
        ---
        Returns trainings as `list` of dictionaries.
        """
        return [sess for sess in self.__mongo.GetTrainings(username)]

    def UpdateTraining(self, username: str, id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single training with new values. 
        ---
        >>> success: bool = data_storage.UpdateTraining("automl_user", sess_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. username: name of the user
        2. id: id of training
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.UpdateTraining(username, id, new_values)


    def SaveDataset(self, username: str, fileName: str, type: str, name: str) -> str:
        """
        Store dataset contents on disk and insert entry to database.
        ---
        >>> id: str = ds.SaveDataset("automl_user", "my_dataset", ...)

        ---
        Parameter
        1. username: name of the user
        2. name: name of dataset
        3. content: raw bytes for file on disk
        4. database_content: dictionary for database
        ---
        Returns dataset id
        """
        analysisResult = {}

        upload_file = os.path.join(self.__storage_dir, username, "uploads", fileName)
        if os.getenv("MONGO_DB_DEBUG") != "YES":
            #Within docker we do not want to add the app section, as this leads to broken links
            upload_file = upload_file.replace("/app/", "")

        #Perform analysis for tabular data datasets
        if type == ":tabular":
            dataset_for_analysis = pd.read_csv(upload_file, engine="python")
            analysisResult = DataSetAnalysisManager.startAnalysis(dataset_for_analysis)


        #build dictionary for database
        database_content = {
            "name": name,
            "type": type,
            "analysis": analysisResult,
            "models": []
        }
        
        dataset_id = self.__mongo.InsertDataset(username, database_content)

        filename_dest = os.path.join(self.__storage_dir, username, dataset_id, fileName)
        if os.getenv("MONGO_DB_DEBUG") != "YES":
            #Within docker we do not want to add the app section, as this leads to broken links
            filename_dest = filename_dest.replace("/app/", "")
        # make sure directory exists in case it's the first upload from this user
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
        
        shutil.move(upload_file, filename_dest)

        #unpack zip file
        if type == ":image":
            shutil.unpack_archive(filename_dest, os.path.join(self.__storage_dir, username, dataset_id))

        #if type == ":image":
        #    shutil

        # fill in missing values
        success = self.__mongo.UpdateDataset(username, dataset_id, {
            "path": filename_dest,
            "mtime": os.path.getmtime(filename_dest)
        })
        assert success, f"cannot update dataset with id {dataset_id}"

        return dataset_id

    def UpdateDataset(self, username: str, id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single dataset with new values. 
        ---
        >>> success: bool = data_storage.UpdateDataset("automl_user", dataset_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. username: name of the user
        2. id: dataset id
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.UpdateDataset(username, id, new_values)


    def FindDataset(self, username: str, identifier: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the _first_ dataset with this name. 
        ---
        >>> found, dataset = ds.FindDataset("automl_user", "my_dataset")
        >>> if not found:
                print("We have a problem")

        ---
        Parameter
        1. username: name of the user
        2. name: name of dataset
        ---
        Returns either `(True, Dataset)` or `(False, None)`.
        """
        result = self.__mongo.FindDataset(username, {
            "_id": ObjectId(identifier)
        })

        return result is not None, result


    def GetDatasets(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user. 
        ---
        >>> for dataset in data_storage.GetDatasets("automl_user"):
                print(dataset["path"])

        ---
        Parameter
        1. username: name of the user
        ---
        Returns `list` of all datasets.
        """
        return [ds for ds in self.__mongo.GetDatasets(username)]


    def InsertModel(self, username: str, model: 'dict[str, object]') -> str:
        """
        Insert single model into the database.
        ---
        >>> mdl_id: str = data_storage.InsertModel("automl_user", {
                "automl_name": "MLJAR",
                "training_id": training_id,
                ...
            })

        ---
        Parameter
        1. username: name of the user
        2. model: dict of model data 
        ---
        Returns id of new model.
        """
        return self.__mongo.InsertModel(username, model)

    def UpdateModel(self, username: str, id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single model with new values. 
        ---
        >>> success: bool = data_storage.UpdateModel("automl_user", model_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. username: name of the user
        2. id: model id
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.UpdateModel(username, id, new_values)

    def GetModels(self, username: str, training_id: str = None, dataset_id: str = None) -> 'list[dict[str, object]]':
        """
        Get all models, or all models by training id or dataset id
        ---
        >>> models = ds.GetModels("automl_user", "training_id")

        ---
        Parameter
        1. username: name of the user
        2. training_id: optinal training id
        2. dataset_id: optinal dataset id
        ---
        Returns a models list
        """
        if training_id != None:
            filter = { "training_id": training_id }
        elif dataset_id != None:
            filter = { "dataset_id": dataset_id }
        else:
            filter = None
        result = self.__mongo.GetModels(username, filter)

        return [ds for ds in result]

    def GetModel(self, username: str, model_id: str = None) -> 'dict[str, object]':
        """
        Get models by model id
        ---
        >>> models = ds.GetModel("automl_user", "model_id")

        ---
        Parameter
        1. username: name of the user
        2. model_id: optinal model id
        ---
        Returns a models list
        """
        return self.__mongo.GetModel(username, model_id)


    class __DbLock():
        """
        DataStore internal helper class. Use with `data_store.lock()`
        """
        def __init__(self, inner: Lock):
            self.__inner = inner
            
        def __enter__(self):
            self.__inner.acquire()
            
        def __exit__(self, type, value, traceback):
            self.__inner .release()
