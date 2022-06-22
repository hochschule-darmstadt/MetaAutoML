
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId
from mongomock import MongoClient as MongoMockClient

class Database:
    """
    MongoDB database interface API.
    ---
    Do not use independently, always use the public DataStorage API.
    ---
    Everything regarding MongoDB should live in this class.
    """

    def __init__(self, server_url="mongodb://root:example@localhost"):
        if server_url is not None:
            self.__mongo = Database.__use_real_database(server_url)
        else:
            self.__mongo = MongoMockClient()


    def __use_real_database(server_url: str) -> MongoClient:
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
                serverSelectionTimeoutMS=3000)
            
            # we want to fail as fast as possible when the database is not reachable.
            #   by default pymongo will lazy initialize and waits for the first 'real' database 
            #   interaction to connect to MongoDB
            mongo.list_databases()

            return mongo
        except:
            raise Exception("cannot find MongoDB!\n    Did you forget to launch it with `docker-compose up --build mongo`?")
        


    def insert_dataset(self, username: str, dataset: 'dict[str, str]') -> str:
        """
        Insert dataset
        ---
        Parameter
        1. username
        2. dataset as dict
        ---
        Returns dataset id
        """
        datasets: Collection = self.__mongo[username]["datasets"]
        result = datasets.insert_one(dataset)
        return str(result.inserted_id)

    def get_datasets(self, username: str) -> 'list[dict[str, object]]':
        """
        Get a dataset byy it"s name
        ---
        Parameter
        1. username
        2. dataset name
        ---
        Returns dataset as dict
        """
        datasets: Collection = self.__mongo[username]["datasets"]
        return datasets.find()

    def find_dataset(self, username: str, filter: 'dict[str, object]') -> 'dict[str, object]':
        """
        Get a dataset by it's name
        ---
        Parameter
        1. username
        2. dataset name
        ---
        Returns dataset as dict or `None`
        """
        datasets: Collection = self.__mongo[username]["datasets"]
        return datasets.find_one(filter)

    def update_dataset(self, username: str, id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update a dataset record
        ---
        Parameter
        1. username
        2. dataset id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        datasets: Collection = self.__mongo[username]["datasets"]
        result = datasets.update_one({ "_id": ObjectId(id) }, { "$set": new_values })
        return result.modified_count >= 1


    def insert_session(self, username: str, session_config: 'dict[str, str]'):
        """
        Insert session
        ---
        Parameter
        1. username
        2. session as dict
        ---
        Returns session id
        """
        sessions: Collection = self.__mongo[username]["sessions"]
        result = sessions.insert_one(session_config)
        return str(result.inserted_id)

    def get_session(self, username: str, id: str) -> 'dict[str, object]':
        """
        Get a session by it's id
        ---
        Parameter
        1. username
        2. session id
        ---
        Returns session as dict
        """
        sessions: Collection = self.__mongo[username]["sessions"]
        return sessions.find_one({ "_id": ObjectId(id) })

    def get_sessions(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all sessions from a user
        ---
        Parameter
        1. username
        ---
        Returns sessions as list of dicts
        """
        sessions: Collection = self.__mongo[username]["sessions"]
        return sessions.find()

    def update_session(self, username: str, id: str, new_values: 'dict[str, str]') -> bool:
        """
        Update a session record
        ---
        Parameter
        1. username
        2. session id
        3. dictionary of new values
        ---
        Returns `True` if a record was updated otherwise `False`
        """
        sessions: Collection = self.__mongo[username]["sessions"]
        result = sessions.update_one({ "_id": ObjectId(id) }, { "$set": new_values })
        return result.modified_count >= 1


    def insert_model(self, username: str, model_details: 'dict[str, str]') -> str:
        """
        Insert model
        ---
        Parameter
        1. username
        2. model as dict
        ---
        Returns model id
        """
        models: Collection = self.__mongo[username]["models"]
        result = models.insert_one(model_details)
        return str(result.inserted_id)

    def get_models(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all models from a user
        ---
        Parameter
        1. username
        ---
        Returns models as list of dicts
        """
        models: Collection = self.__mongo[username]["models"]
        return models.find()


    def drop_database(self, username: str):
        """
        Delete all datasets sessions and models for a user
        ---
        Parameter
        1. username
        """
        self.__mongo.drop_database(username)
