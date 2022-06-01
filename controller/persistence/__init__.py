import os, os.path
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
    def __init__(self, data_storage_dir):
        # ensure folder exists
        os.makedirs(data_storage_dir, exist_ok=True)

        self.__storage_dir = data_storage_dir

        # assume that we run with docker-compose
        self.__mongo: Database = Database("mongodb://root:example@mongo")


    def insert_session(self, username: str, config: 'dict[str, str]') -> str:
        result = self.__mongo.insert_session(username, config)
        print(f"inserted session: '{result.inserted_id}'")

        return str(result.inserted_id)


    def save_dataset(self, username: str, name: str, content: bytes):
        filename_dest = os.path.join(self.__storage_dir, name)
        save_file = open(filename_dest, 'wb')
        save_file.write(content)

        self.__mongo.insert_dataset(username, name, filename_dest)
        print(f"inserted dataset '{name}'")


    def get_dataset(self, username: str, name: str) -> Dataset:

        dataset = self.__mongo.get_dataset(username, name)
        if dataset is None: 
            # dataset path does not exist in database
            raise Exception(f"cannot find dataset: '{name}'")


        filepath: str = dataset["path"]

        if not os.path.exists(filepath):
            # dataset path does not exist on disk
            # TODO: what to do in case of error, database cleanup?
            raise FileNotFoundError

        mtime = os.path.getmtime(filepath)

        return Dataset(name, filepath, mtime)


    def get_datasets(self, username: str) -> 'Iterator[Dataset]':
        
        for result in self.__mongo.get_datasets(username):
            name, filepath = itemgetter("name", "path")(result)

            if not os.path.exists(filepath):
                # dataset path does not exist
                # TODO: what to do in case of error, database cleanup?
                raise FileNotFoundError

            mtime = os.path.getmtime(filepath)
            yield Dataset(name, filepath, mtime)


    def insert_model(self, username: str, model_details):
        result = self.__mongo.insert_model(username, model_details)
        print(f"inserted model '{result.inserted_id}'")

        return str(result.inserted_id)
