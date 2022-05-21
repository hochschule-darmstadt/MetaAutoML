
from pymongo import MongoClient
from pymongo.collection import Collection

# sample credentials from docker-compose
# NOTE: when running this script in a container defined in docker-compose.yml,
#       the url for MongoClient needs to match the database service name
#       --> eg. "mongodb://root:example@mongo"
client = MongoClient("mongodb://root:example@localhost", 27017)

# create new database
db=client["automl"]

# create new collections, similar to tables in relatonal dbs
datasets: Collection = db["datasets"]
trainings: Collection = db["trainings"]
models: Collection = db["models"]


# ---- create

result = datasets.insert_one({
    "id": "dataset001",
    "name": "titanic.csv",
    "user_id": "acb123",
    "path": "/tmp/titanic.csv",
    "analysis": { 
        # provided by dataset analysis team
        "noideawhatthisis": True 
    },
    "creation_date": "2022-05-18 10:25"
})
print(f"dataset id {result.inserted_id}")

result = trainings.insert_one({
    "id": "training001",
    "start_date": "",
    "end_date": "",
    "configuration": { 
        "somejson": True
    },
    "status": "running"
})
print(f"training id {result.inserted_id}")

result = models.insert_one({
    "id": "model001",
    "configuration": { 
        "somejson": True
    },
    "predictiontime": 12345.67,
    "metric_score": 0.001
})
print(f"model id {result.inserted_id}")

print();print()


# ---- read

result = datasets.find_one({ "id": "dataset001" })
print(f"found dataset with name: {result['name']}")

result = trainings.find_one({ "id": "training001" })
print(f"found dataset with configuration: {result['configuration']}")

result = models.find_one({ "id": "model001" })
print(f"found model with predictiontime: {result['predictiontime']}")