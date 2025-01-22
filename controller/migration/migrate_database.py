from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection
from pymongo import ASCENDING

SERVER_URL = "mongodb://root:example@localhost/"
USER_ID = "080a6480-bf52-4c30-9224-3f2b882fd5bb"
MODE = "PROD" # PROD or TEST

mongo = MongoClient(SERVER_URL, 27017,
                # timeout to find a database server
                serverSelectionTimeoutMS=30000)

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
                print(f"Index: {index_name}")
                print(f"Index Info: {index_info}")
                if index_name != '_id_':
                    keys = index_info['key']
                    options = {k: v for k, v in index_info.items()
                                if k not in ['key', 'v', 'ns']}
                    print(f"Creating index {index_name} on {collection_name}")
                    target_db[collection_name].create_index(keys, **options)

# Copy views
for view_name in source_db.list_collection_names(filter={"type": "view"}):
    print(f"Processing view: {view_name}")

    # Get view definition and print it for debugging
    view_info = source_db.command({
        "listCollections": 1,
        "filter": {
            "name": view_name,
            "type": "view"
        }
    })

    view_def = view_info["cursor"]["firstBatch"][0]
    print("View definition:", view_def)  # Let's see what we have

    # Create view in target database using the correct keys
    target_db.command({
        "create": view_name,
        "viewOn": view_def.get("options", {}).get("viewOn"),  # Try to get from options
        "pipeline": view_def.get("options", {}).get("pipeline")
    })
    print(f"Created view: {view_name}")

print("Database and indexes cloned successfully!")
print("\nVerification:")
print("Available databases:", mongo.list_database_names())
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

print("Creating index on dataset_id")
current_db['models'].create_index([('dataset_id', ASCENDING)])
