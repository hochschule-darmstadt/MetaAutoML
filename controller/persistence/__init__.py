from threading import Lock
import os
import os.path
from persistence.mongo_client import Database


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
            self.__mongo: Database = database

        self.__lock = Lock()


    def lock(self):
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


    def insert_session(self, username: str, session: 'dict[str, object]') -> str:
        """
        Insert single session into the database.
        ---
        >>> id: str = ds.insert_session("automl_user", {
                "dataset": ...,
                ...
            })

        ---
        Parameter
        1. username: name of the user
        2. session: session dict to be inserted
        ---
        Returns session id
        """
        return self.__mongo.insert_session(username, session)


    def get_session(self, username: str, id: str) -> 'dict[str, object]':
        """
        Get single session by id. 
        ---
        >>> sess = data_storage.get_session("automl_user", sess_id)
        >>> if sess is None:
                raise Exception("cannot find session")
        
        ---
        Parameter
        1. username: name of the user
        2. id: id of session
        ---
        Returns session as `dict` or `None` if not found.
        """
        return self.__mongo.get_session(username, id)

    def get_sessions(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all sessions for a user. 
        ---
        >>> for sess in data_storage.get_sessions("automl_user"):
                print(sess["dataset"])

        ---
        Parameter
        1. username: name of the user
        ---
        Returns sessions as `list` of dictionaries.
        """
        return [sess for sess in self.__mongo.get_sessions(username)]

    def update_session(self, username: str, id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single session with new values. 
        ---
        >>> success: bool = data_storage.update_session("automl_user", sess_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. username: name of the user
        2. id: id of session
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.update_session(username, id, new_values)


    def save_dataset(self, username: str, name: str, content: bytes) -> str:
        """
        Store dataset contents on disk and insert entry to database.
        ---
        >>> id: str = ds.save_dataset("automl_user", "my_dataset", ...)

        ---
        Parameter
        1. username: name of the user
        2. name: name of dataset
        3. content: raw bytes for file on disk
        ---
        Returns dataset id
        """

        # insert shell entry first to get id from database
        dataset_id = self.__mongo.insert_dataset(username, {
            "name": name,

            # we need the dataset id from the database for these fields
            "path": "",
            "mtime": 0.0
        })

        filename_dest = os.path.join(self.__storage_dir, username, dataset_id)
        # make sure directory exists in case it's the first upload from this user
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
        with open(filename_dest, 'wb') as outfp:
            outfp.write(content)

        # fill in missing values
        success = self.__mongo.update_dataset(username, dataset_id, {
            "path": filename_dest,
            "mtime": os.path.getmtime(filename_dest)
        })
        assert success, f"cannot update session with id {dataset_id}"

        return dataset_id


    def find_dataset(self, username: str, name: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the _first_ dataset with this name. 
        ---
        >>> found, dataset = ds.find_dataset("automl_user", "my_dataset")
        >>> if not found:
                print("We have a problem")

        ---
        Parameter
        1. username: name of the user
        2. name: name of dataset
        ---
        Returns either `(True, Dataset)` or `(False, None)`.
        """
        result = self.__mongo.find_dataset(username, {
            "name": name
        })

        return result is not None, result


    def get_datasets(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user. 
        ---
        >>> for dataset in data_storage.get_datasets("automl_user"):
                print(dataset["path"])

        ---
        Parameter
        1. username: name of the user
        ---
        Returns `list` of all datasets.
        """
        return [ds for ds in self.__mongo.get_datasets(username)]


    def insert_model(self, username: str, model: 'dict[str, object]') -> str:
        """
        Insert single model into the database.
        ---
        >>> mdl_id: str = data_storage.insert_model("automl_user", {
                "automl_name": "MLJAR",
                "session_id": session_id,
                ...
            })

        ---
        Parameter
        1. username: name of the user
        2. model: dict of model data 
        ---
        Returns id of new model.
        """
        return self.__mongo.insert_model(username, model)



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
