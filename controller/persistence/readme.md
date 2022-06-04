The MognoDB script is supposed to run alongside the database container defined in docker-compose.

* start database containers with: `docker-compose up --build mongo neo4j`
* run scripts with `python3 poc_mongo.py`

Run the cli in Python REPL with `python3 -i cli.py`


## Tests
Tests can be run with `/usr/local/bin/python controller/persistence/test_datastore.py`. Docker containers do not need to be running, MongoDB Mock is used to mimick database access.