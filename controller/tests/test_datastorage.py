
# add parent folder tot system path so python will find persistence package
import sys
from pathlib import Path
from time import sleep

from numpy import tracemalloc_domain

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))
try:
    sys.path.remove(str(parent))
except ValueError:
    # Already removed
    pass


import unittest
from persistence.data_storage import DataStorage
from persistence.mongo_client import Database
import threading 

class TestDataStorage(unittest.TestCase):
    
    def test_save_dataset(self):
        """
        Test Dataset Insertion
        ---
        """

        database = Database(server_url=None)
        database.drop_database("test_user")

        data_storage = DataStorage("/tmp/data_storage_test", database)

        # titanic dataset
        file_contents = b"""PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked
1,0,3,"Braund, Mr. Owen Harris",male,22,1,0,A/5 21171,7.25,,S
2,1,1,"Cumings, Mrs. John Bradley (Florence Briggs Thayer)",female,38,1,0,PC 17599,71.2833,C85,C
3,1,3,"Heikkinen, Miss. Laina",female,26,0,0,STON/O2. 3101282,7.925,,S
4,1,1,"Futrelle, Mrs. Jacques Heath (Lily May Peel)",female,35,1,0,113803,53.1,C123,S
5,0,3,"Allen, Mr. William Henry",male,35,0,0,373450,8.05,,S
6,0,3,"Moran, Mr. James",male,,0,0,330877,8.4583,,Q
7,0,1,"McCarthy, Mr. Timothy J",male,54,0,0,17463,51.8625,E46,S
8,0,3,"Palsson, Master. Gosta Leonard",male,2,3,1,349909,21.075,,S
"""
        id: str = data_storage.save_dataset("test_user", "test_dataset.csv", file_contents)
        assert id is not None and len(id) > 0, "Dataset ID is None or empty"


        # check single dataset
        found, from_db = data_storage.find_dataset("test_user", "test_dataset.csv")
        assert found, "Could not find dataset in database"
        assert from_db["name"] == "test_dataset.csv", "Wrong dataset name in database"
        assert from_db["path"].endswith(f"test_user/{id}"), "Wrong dataset path in database"

        with open(from_db["path"], "rb") as fpin:
            from_disk = fpin.read()
            assert file_contents == from_disk, "File contents do not match"


        # check all datasets
        datasets = data_storage.get_datasets("test_user")
        assert len(datasets) == 1, "Datasets was not inserted"

        for i in range(5):
            data_storage.save_dataset("test_user", str(i), file_contents)

        datasets = data_storage.get_datasets("test_user")
        assert len(datasets) == 6, "Some Datasets were not inserted"

        ids = list(map(lambda d: d["_id"], datasets))
        assert len(ids) == len(set(ids)), "Dataset IDs are not unique"


    def test_insert_session(self):
        """
        Test Session Insertion
        ---
        """

        database = Database(server_url=None)
        database.drop_database("test_user")

        data_storage = DataStorage("/tmp/data_storage_test", database)

        # check single session
        session = {
            "dataset":"titanic_train_1.csv",
            "task":1,
            "tabularConfig":{
                "target":{
                    "target":"Survived",
                    "type":5
                },
                "features":{
                    "Sex": 4,
                }
            },
            "fileConfiguration":{
                "sep":","
            },
            "metric":"",
            "status":"running",
            "models":[ ]
        }
        sess_id = data_storage.insert_session("test_user", session)
        assert sess_id is not None and len(sess_id) > 0, "Session ID is None or empty"
        print("sess_id:", sess_id)


        from_database = data_storage.get_session("test_user", sess_id)
        assert session == from_database, "Session in database does not match"

        sessions = data_storage.get_sessions("test_user")

        # check multiple sessions
        for i in range(5):
            # NOTE: we cannot reuse session dict here, MongoDB will complain with:
            #       E11000 Duplicate Key Error
            #  * possibly connected to how python stores nested dictionaires, but not sure
            #  * in production we will never try to insert the same session dict, so not really relevant
            data_storage.insert_session("test_user", {
                "dataset":"titanic_train_1.csv",
                "task":1,
                "tabularConfig":{
                    "target":{
                        "target":"Survived",
                        "type":5
                    },
                    "features":{
                        "Sex": 69,
                    }
                },
                "fileConfiguration":{
                    "sep":","
                },
                "metric":"",
                "status":"running",
                "models":[ ]
            })

        sessions = data_storage.get_sessions("test_user")
        assert len(sessions) == 6, "Some Sessions were not inserted"

        ids = list(map(lambda s: s["_id"], sessions))
        assert len(ids) == len(set(ids)), "Session IDs are not unique"


    def test_update_session(self):
        """
        Test Session Update
        ---
        """

        database = Database(server_url=None)
        database.drop_database("test_user")

        data_storage = DataStorage("/tmp/data_storage_test", database)

        session = {
            "dataset": "titanic_train_1.csv",
            "task":1,
            "tabularConfig":{
                "target":{
                    "target":"Survived",
                    "type":5
                },
                "features":{
                    "Sex": 4,
                }
            },
            "fileConfiguration":{
                "sep":","
            },
            "metric":"",
            "status":"running",
            "models":[ ]
        }
        sess_id = data_storage.insert_session("test_user", session)

        # update and refetch
        data_storage.update_session("test_user", sess_id, { "status": "done" })
        from_database = data_storage.get_session("test_user", sess_id)
        assert from_database["status"] == "done", "Session was not updated"


        # update and refetch
        data_storage.update_session("test_user", sess_id, { "models": [ 1 ] })
        from_database = data_storage.get_session("test_user", sess_id)
        assert len(from_database["models"]) == 1, "Session was not updated correctly"

        # update and refetch
        data_storage.update_session("test_user", sess_id, { "models": [ 1, 2 ] })
        from_database = data_storage.get_session("test_user", sess_id)
        assert len(from_database["models"]) == 2, "Session was not updated correctly"

    def test_insert_model(self):
        """
        Test Model Insertion
        ---
        """

        database = Database(server_url=None)
        database.drop_database("test_user")

        data_storage = DataStorage("/tmp/data_storage_test", database)

        # check single model
        model = {
            "automl_name": "AutoGluon",
            "session_id": "629bc1b7d4a68ec6443716cd",
            "path": "app-data/output/gluon/629bc1b7d4a68ec6443716cd/gluon-export.zip",
            "test_score": 0.826815664768219,
            "validation_score": 0.0,
            "runtime": 6,
            "model": "WeightedEnsemble_L2",
            "library": "sklearn"
        }
        mdl_id = data_storage.insert_model("test_user", model)
        assert mdl_id is not None and len(mdl_id) > 0


    def test_concurrent_access(self):
        """
        Test Database Locking
        ---
        This is an example for concurrently appending a list in the database.
        We fetch a record, manipulate it and then write it back to the database.
        """

        database = Database(server_url=None)
        database.drop_database("test_user")

        data_storage = DataStorage("/tmp/data_storage_test", database)

        sess_id = data_storage.insert_session("test_user", {
            # skip other fields for clarity
            "models": [ 1 ]
        })


        # helper function for database access
        #   will run in parallel
        def access_db(data_storage):
            with data_storage.lock():
                # get same session object inserted above and make changes
                from_db = data_storage.get_session("test_user", sess_id)
                data_storage.update_session("test_user", sess_id, { 
                    # append another value to the list
                    "models": from_db["models"] + [ 1 ]
                })

                expected_model_count = len(from_db["models"]) + 1

                # wait a bit for other threads to make changes
                sleep(0.1)

                from_db = data_storage.get_session("test_user", sess_id)
                assert len(from_db["models"]) == expected_model_count, "exclusive database access does not work"


        # build, spawn and sync all threads
        threads: threading.Thread = []
        for i in range(10):
            threads.append(threading.Thread(target=access_db, args=[data_storage]))

        for th in threads:
            th.start()

        for th in threads:
            th.join()

if __name__ =='__main__':
    unittest.main()
