
from pymongo import MongoClient
from pymongo.collection import Collection

class Database:
    def __init__(self, server_url="mongodb://root:example@localhost"):
        # sample credentials from docker-compose
        # NOTE: when running this script in a container defined in docker-compose.yml,
        #       the url for MongoClient needs to match the database service name
        #       --> eg. "mongodb://root:example@mongo"
        self.mongo = MongoClient(server_url, 27017)
        pass

    def get_dataset(self, username: str, name: str):
        # will auto create database if it does not exist
        database = self.mongo[username]
        datasets: Collection = database["datasets"]
        return datasets.find_one({ "name": name })


    def get_datasets(self, username: str):
        # will auto create database if it does not exist
        database = self.mongo[username]
        datasets: Collection = database["datasets"]
        return datasets.find()


    def insert_dataset(self, username: str, name: str, file_path: str):
        database = self.mongo[username]
        datasets: Collection = database["datasets"]
        return datasets.insert_one({ "name": name, "path": file_path })
            