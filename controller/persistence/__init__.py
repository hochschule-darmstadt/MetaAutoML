from threading import Lock
import os
import os.path
from typing import Iterator
from persistence.mongo_client import Database
from operator import itemgetter


class Dataset:
    def __init__(self, name: str, path: str, mtime: float):
        self.name = name
        self.path = path
        self.mtime = mtime

    def __repr__(self) -> str:
        return f"Dataset: \"{self.name}\"  -->  \"{self.path}\")"


class DataStorage:
    class __DbLock():
        """DataStore internal helper class"""
        def __init__(self, inner: Lock):
            self.__inner = inner
            
        def __enter__(self):
            self.__inner.acquire()
            
        def __exit__(self, type, value, traceback):
            self.__inner .release()


    def __init__(self, data_storage_dir: str):
        # ensure folder exists
        os.makedirs(data_storage_dir, exist_ok=True)

        self.__storage_dir = data_storage_dir

        # assume that we run with docker-compose
        self.__mongo: Database = Database("mongodb://root:example@mongo")
        self.__lock = Lock()

    def lock(self):
        """lock access to the data storage to a single thread
        >>> with datastore.lock():
                # critical region
                sess = data_storage.get_session(...)
                data_storage.update_session(..., {
                    "models": sess["models"] + [new_model]
                })
        >>> # code that can run parallel
        """
        return DataStorage.__DbLock(self.__lock)

    def insert_session(self, username: str, session: 'dict[str, object]') -> str:
        """insert session to users collection"""
        result = self.__mongo.insert_session(username, session)
        print(f"inserted session: '{result.inserted_id}'")

        return str(result.inserted_id)

    def get_session(self, username: str, id: str) -> 'dict[str, object]':
        session: dict[str, object] = self.__mongo.get_session(username, id)

        if session is None:
            raise Exception(f"cannot find session: '{id}'")

        return session

    def update_session(self, username: str, id: str, new_values : 'dict[str, object]') -> bool:
        """update single session with new values"""
        result = self.__mongo.update_session(username, id, new_values)
        if result.modified_count >= 1:
            print(f"updated session: '{id}'")
        
        return result.modified_count >= 1
        

    def save_dataset(self, username: str, name: str, content: bytes) -> str:
        """store dataset contents on disk and insert entry to database"""
        filename_dest = os.path.join(self.__storage_dir, username, name)

        # make sure directory exists in case it's the first upload from this user
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
        with open(filename_dest, 'wb') as outfp:
            outfp.write(content)

        mtime = os.path.getmtime(filename_dest)

        # TODO: can datasets be replaced?
        # name is not primary key, so same dataset will be inserted twice
        result = self.__mongo.insert_dataset(username, {
            "name": name,
            "path": filename_dest,
            "mtime": mtime
        })
        print(f"inserted dataset '{name}'")

        return str(result)

    def get_dataset(self, username: str, name: str) -> Dataset:
        """return dataset with specified name"""
        dataset: dict[str, object] = self.__mongo.get_dataset(username, name)

        if dataset is None:
            # dataset path does not exist in database
            raise Exception(f"cannot find dataset: '{name}'")

        return self.__upgrade_dataset(dataset)

    def __upgrade_dataset(self, from_database: 'dict[str, object]') -> Dataset:
        """convert raw database dictionary to Dataset"""
        # get values from dict
        name: str = from_database["name"]
        filepath: str = from_database["path"]
        mtime: float = from_database["mtime"]

        if not os.path.exists(filepath):
            # dataset path does not exist on disk
            # TODO: what to do in case of error, database cleanup?
            raise FileNotFoundError

        return Dataset(name, filepath, mtime)

    def get_datasets(self, username: str) -> 'Iterator[Dataset]':
        """return all datasets for this user"""
        for raw_dict in self.__mongo.get_datasets(username):
            yield self.__upgrade_dataset(raw_dict)

    def insert_model(self, username: str, model: 'dict[str, object]') -> str:
        """insert model to users collection"""
        result = self.__mongo.insert_model(username, model)
        print(f"inserted model '{result.inserted_id}'")

        return str(result.inserted_id)
