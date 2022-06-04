
# add parent folder tot system path so python will find persistence package
from re import A
import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))
try:
    sys.path.remove(str(parent))
except ValueError:
    # Already removed
    pass


import unittest
from persistence import DataStorage
from persistence.mongo_client import Database

class TestRdfManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database = Database(server_url=None)
        database.drop_database("test_user")

        cls.data_storage = DataStorage("/tmp/data_storage_test", database)


    def test_save_dataset(self):
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
        id: str = self.data_storage.save_dataset("test_user", "test_dataset.csv", file_contents)
        assert id is not None and len(id) > 0
        

        # check single dataset
        found, from_db = self.data_storage.find_dataset("test_user", "test_dataset.csv")
        assert found, "find failed"
        assert from_db["name"] == "test_dataset.csv"
        assert from_db["path"].endswith(f"test_user/{id}")

        with open(from_db["path"], "rb") as fpin:
            from_disk = fpin.read()
            assert file_contents == from_disk


        # check all datasets
        datasets = self.data_storage.get_datasets("test_user")
        assert len(datasets) == 1

        for i in range(5):
            self.data_storage.save_dataset("test_user", str(i), file_contents)

        datasets = self.data_storage.get_datasets("test_user")
        assert len(datasets) == 6


    def test_insert_session(self):
        # restructure configuration into python dictionaries
        session = {
            "dataset":"titanic_train_1.csv",
            "task":1,
            "tabularConfig":{
                "target":{
                    "target":"Survived",
                    "type":5
                },
                "features":{
                    "Sex":4,
                    "PassengerId":7,
                    "Embarked":4,
                    "Cabin":7,
                    "Name":7,
                    "Fare":3,
                    "Age":3,
                    "SibSp":2,
                    "Pclass":4,
                    "Ticket":7,
                    "Parch":2
                }
            },
            "fileConfiguration":{
                "sep":","
            },
            "metric":"",
            "status":"running",
            "models":[ ]
        }
        sess_id = self.data_storage.insert_session("test_user", session)
        assert sess_id is not None and len(sess_id) > 0

        from_database = self.data_storage.get_session("test_user", sess_id)
        assert session == from_database


    def test_insert_model(self):
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
        mdl_id = self.data_storage.insert_model("test_user", model)
        assert mdl_id is not None and len(mdl_id) > 0


if __name__ =='__main__':
    unittest.main()