from threading import Lock
import os
import os.path
from persistence.mongo_client import Database


class DataStorage:
    """Centralized Access to File System and Database"""


    def __init__(self, data_storage_dir: str, database = None):
        """
        Initialize new instance. This should be done already.
        Do _not_ use multiple instances of this class.

        Will connect to the MongoDB database defined in docker-compose
        unless `database` is provided.

        >>> data_storage = DataStorage("/tmp/")
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
        Insert single session into the database. Returns session id.
        
        >>> id: str = ds.insert_session("automl_user", {
                "dataset": ...,
                ...
            })
        """
        return self.__mongo.insert_session(username, session)


    def get_session(self, username: str, id: str) -> 'dict[str, object]':
        """
        Get single session by id. Returns session as `dict` or `None` if not found.

        >>> sess = data_storage.get_session("automl_user", sess_id)
        >>> if sess is None:
                throw Exception("cannot find session")
        """
        return self.__mongo.get_session(username, id)


    def update_session(self, username: str, id: str, new_values : 'dict[str, object]') -> bool:
        """
        Update single session with new values. Returns `True` if successfully updated, otherwise `False`.
        
        >>> success: bool = data_storage.update_session("automl_user", sess_id, {
                "status": "completed"
            })
        """
        return self.__mongo.update_session(username, id, new_values)


    def save_dataset(self, username: str, name: str, content: bytes) -> str:
        """
        Store dataset contents on disk and insert entry to database.

        >>> id: str = ds.save_dataset("automl_user", "my_dataset", ...)
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
        Try to find the _first_ dataset with this name. Returns either `(True, Dataset)` or `(False, None)`.

        >>> found, dataset = ds.find_dataset("automl_user", "my_dataset")
        >>> if not found:
                print("We have a problem")
        """
        result = self.__mongo.find_dataset(username, {
            "name": name
        })

        return result != None, result


    def get_datasets(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user. Returns `list` of all datasets.
        
        >>> for dataset in data_storage.get_datasets("automl_user"):
                print(dataset["path"])
        """
        return [ds for ds in self.__mongo.get_datasets(username)]


    def insert_model(self, username: str, model: 'dict[str, object]') -> str:
        """
        Insert single model tinto the database. Returns id of new model.
        
        >>> mdl_id: str = data_storage.insert_model("automl_user", {
                "automl_name": "MLJAR",
                "session_id": session_id,
                ...
            })
        """
        return self.__mongo.insert_model(username, model)



    class __DbLock():
        """DataStore internal helper class. Use with `data_store.lock()`"""
        def __init__(self, inner: Lock):
            self.__inner = inner
            
        def __enter__(self):
            self.__inner.acquire()
            
        def __exit__(self, type, value, traceback):
            self.__inner .release()

