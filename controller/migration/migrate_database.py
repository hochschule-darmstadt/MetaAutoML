from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING

SERVER_URL = "mongodb://root:example@localhost/"
USER_ID = "080a6480-bf52-4c30-9224-3f2b882fd5bb"
MODE = "TEST" # PROD or TEST

mongo = MongoClient(SERVER_URL, 27017, serverSelectionTimeoutMS=30000)

mongo.list_databases()

source_db = mongo[USER_ID]
target_db = mongo[USER_ID + "_test"]

for collection_name in source_db.list_collection_names(filter={"type": "collection"}):
    if not collection_name.startswith('system.'):
        print(f"Copying collection: {collection_name}")

        source_collection = source_db[collection_name]
        index_info = source_collection.index_information()

        documents = source_collection.find()
        count = source_collection.count_documents({})
        print(f"Documents: {count}")
        if count > 0:
            target_db[collection_name].insert_many(documents)

            # Create indexes (skip _id_ index as it's created automatically)
            for index_name, index_info in index_info.items():
                if index_name != '_id_':
                    keys = index_info['key']
                    options = {k: v for k, v in index_info.items()
                                if k not in ['key', 'v', 'ns']}
                    print(f"Creating index {index_name} on {collection_name}")
                    target_db[collection_name].create_index(keys, **options)

for view_name in source_db.list_collection_names(filter={"type": "view"}):
    view_info = source_db.command({
        "listCollections": 1,
        "filter": {
            "name": view_name,
            "type": "view"
        }
    })

    view_def = view_info["cursor"]["firstBatch"][0]

    target_db.command({
        "create": view_name,
        "viewOn": view_def.get("options", {}).get("viewOn"),
        "pipeline": view_def.get("options", {}).get("pipeline")
    })
    print(f"Created view: {view_name}")

print("Database and indexes cloned successfully!")
print("\nVerification:")
if USER_ID + '_test' in mongo.list_database_names():
    print("Target database collections:", target_db.list_collection_names())
else:
    print("Target database was not created!")

if MODE == "PROD":
    current_db = source_db
elif MODE == "TEST":
    current_db = target_db

pipeline = [
    {
        '$lookup': {
            'from': 'trainings',
            'let': {
                'trainingId': '$training_id'
            },
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$eq': [
                                {
                                    '$toString': '$_id'
                                }, '$$trainingId'
                            ]
                        }
                    }
                }
            ],
            'as': 'training'
        }
    }, {
        '$unwind': {
            'path': '$training',
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$addFields': {
            'dataset_id': {
                '$toObjectId': '$training.dataset_id'
            }
        }
    }, {
        '$project': {
            'dataset_id': 1
        }
    }
]

result = list(current_db['models'].aggregate(pipeline))

updates = [
   UpdateOne(
       {'_id': doc['_id']},
       {'$set': {'dataset_id': doc['dataset_id']}}
   ) for doc in result
]

print(f"Updating {len(updates)} documents")
current_db['models'].bulk_write(updates)

print("Creating indexes")
datasets = current_db['datasets']
datasets.create_index([("analysis.creation_date", DESCENDING)])
datasets.create_index([("lifecycle_state", ASCENDING)])
datasets.create_index([("_id", ASCENDING)])

models = current_db['models']
models.create_index([('dataset_id', ASCENDING)])
models.create_index([("training_id", ASCENDING)])
models.create_index([("lifecycle_state", ASCENDING)])
models.create_index([("_id", ASCENDING)])

trainings = current_db['trainings']
trainings.create_index([("dataset_id", ASCENDING)])
trainings.create_index([("runtime_profile.start_time", DESCENDING)])
trainings.create_index([("lifecycle_state", ASCENDING)])
trainings.create_index([("_id", ASCENDING)])

predictions = current_db['predictions']
predictions.create_index([("model_id", ASCENDING)])
predictions.create_index([("lifecycle_state", ASCENDING)])
predictions.create_index([("_id", ASCENDING)])

print("Migration completed successfully!")
