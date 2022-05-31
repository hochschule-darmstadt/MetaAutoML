
from mongo_client import Database

username = "automl_user"
# assume that we run outside of docker-compose
mongo: Database = Database("mongodb://root:example@localhost")


get_datasets = lambda: mongo.get_datasets(username)
get_sessions = lambda: mongo.get_sessions(username)

datasets = [(ds["name"], ds["path"]) for ds in get_datasets()]
print(f"found {len(datasets)} datasets:")
for name, path in datasets:
    print(f"  {name}:\t'{path}'")

sessions = [sess for sess in get_sessions()]
print(f"found {len(sessions)} sessions:")
for sess in sessions:
    print(f"  {sess['session_id']}")