
#
# Run the cli in Python REPL with `python3 -i cli.py`
#

# add parent folder to system path so python will find persistence package
import sys
import os
from pathlib import Path

# add controller directory to system path, so Python can find modules
file = Path(__file__).resolve()
sys.path.append(os.path.join(file.parents[2]))

from persistence.mongo_client import Database

username = "automl_user"
# assume that we run outside of docker-compose
mongo: Database = Database("mongodb://root:example@localhost")


get_datasets = lambda: [ds for ds in mongo.get_datasets(username)]
get_sessions = lambda: [sess for sess in mongo.get_sessions(username)]
get_models = lambda: [mdl for mdl in mongo.get_models(username)]
drop_database = lambda: mongo.drop_database(username)

datasets = get_datasets()
print(f"found {len(datasets)} datasets:")
for ds in datasets:
    print(f"  {ds['name']}:\t'{ds['path']}'")

sessions = get_sessions()
print(f"found {len(sessions)} sessions:")
for sess in sessions:
    print(f"  {sess['_id']}")


models = get_models()
print(f"found {len(models)} models:")
for model in models:
    print(f"  {model['path']}")
