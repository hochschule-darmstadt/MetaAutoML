The MognoDB script is supposed to run alongside the database container defined in docker-compose.

* start database containers with: `docker-compose up --build mongo neo4j`
* run scripts with `python3 poc_mongo.py`