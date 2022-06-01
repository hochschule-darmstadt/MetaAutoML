
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId


class Database:
    """MongoDB database interface API"""
    def __init__(self, server_url="mongodb://root:example@localhost"):
        # sample credentials from docker-compose
        # NOTE: when running this script in a container defined in docker-compose.yml,
        #       the url for MongoClient needs to match the database service name
        #       --> eg. "mongodb://root:example@mongo"
        self.mongo = MongoClient(server_url, 27017)
        pass

    def get_dataset(self, username: str, name: str):
        database = self.mongo[username]
        datasets: Collection = database["datasets"]
        return datasets.find_one({"name": name})

    def get_datasets(self, username: str):
        database = self.mongo[username]
        datasets: Collection = database["datasets"]
        return datasets.find()

    def insert_dataset(self, username: str, dataset: 'dict[str, str]'):
        database = self.mongo[username]
        datasets: Collection = database["datasets"]
        return datasets.insert_one(dataset)

    def insert_session(self, username: str, session_config: 'dict[str, str]'):
        database = self.mongo[username]
        sessions: Collection = database["sessions"]
        return sessions.insert_one(session_config)

    def get_session(self, username: str, id: str):
        database = self.mongo[username]
        sessions: Collection = database["sessions"]
        return sessions.find_one({ "_id": ObjectId(id) })

    def update_session(self, username: str, id: str, new_values: 'dict[str, str]'):
        database = self.mongo[username]
        sessions: Collection = database["sessions"]
        return sessions.update_one({ "_id": ObjectId(id) }, { "$set": new_values})

    def get_sessions(self, username: str):
        database = self.mongo[username]
        sessions: Collection = database["sessions"]
        return sessions.find()

    def insert_model(self, username: str, model_details):
        database = self.mongo[username]
        models: Collection = database["models"]
        return models.insert_one(model_details)

    def get_models(self, username: str):
        database = self.mongo[username]
        models: Collection = database["models"]
        return models.find()

    def drop_database(self, username: str):
        self.mongo.drop_database(username)
