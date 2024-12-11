from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId

class MongoDbDocuments:
    def __init__(self, client):
        self.client = client

    def setup_collections(self, db_name):
        self.db = self.client[db_name]
        self.setup_datasets_collection()
        self.setup_models_collection()
        self.setup_trainings_collection()
        self.setup_predictions_collection()
        self.setup_views()

    def setup_datasets_collection(self):
        datasets = self.db['datasets']
        datasets.create_index([("analysis.creation_date", DESCENDING)])
        datasets.create_index([("lifecycle_state", ASCENDING)])
        datasets.create_index([("_id", ASCENDING)])

    def setup_models_collection(self):
        models = self.db['models']
        models.create_index([("training_id", ASCENDING)])
        models.create_index([("lifecycle_state", ASCENDING)])
        models.create_index([("_id", ASCENDING)])

    def setup_trainings_collection(self):
        trainings = self.db['trainings']
        trainings.create_index([("dataset_id", ASCENDING)])
        trainings.create_index([("runtime_profile.start_time", DESCENDING)])
        trainings.create_index([("lifecycle_state", ASCENDING)])
        trainings.create_index([("_id", ASCENDING)])

    def setup_predictions_collection(self):
        predictions = self.db['predictions']
        predictions.create_index([("model_id", ASCENDING)])
        predictions.create_index([("lifecycle_state", ASCENDING)])
        predictions.create_index([("_id", ASCENDING)])

    def setup_views(self):
        self.db.command({
            "create": "active_datasets",
            "viewOn": "datasets",
            "pipeline": [
                {"$match": {"lifecycle_state": "active"}}
            ]
        })

if __name__ == "__main__":
    client = MongoClient("mongodb://root:example@localhost")
    mongo_docs = MongoDbDocuments(client)
    mongo_docs.setup_collections("MetaAutoML")
