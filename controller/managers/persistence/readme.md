These scripts are supposed to run alongside the database containers defined in docker-compose.

* start database containers with: `docker-compose up --build mongo neo4j`
* run scripts with `python3 poc_neo4j.py` or `python3 poc_mongo.py`