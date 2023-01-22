import json
import os
import shutil
import unittest
from unittest import IsolatedAsyncioTestCase
import uuid

import pandas as pd
from EvalMLAdapterManager import EvalMLAdapterManager
from Container import *
from AdapterBGRPC import *

def load_titanic_dataset():
    """download titanic dataset
    Returns:
        path of reduced dataset csv
    """
    cache_dir = os.path.join("tests", "datasets")
    os.makedirs(cache_dir, exist_ok=True)
    titanic: pd.DataFrame = pd.read_csv(filepath_or_buffer="https://storage.googleapis.com/tf-datasets/titanic/train.csv",)

    # drop other columns for simplicity
    titanic = titanic[["age", "sex", "survived"]]

    dataset_path = os.path.join(cache_dir, "titanic.csv")
    with open(dataset_path, "w+") as outfp:
        pd.DataFrame.to_csv(titanic, outfp, index=False)

    return dataset_path

class TestAdapter(IsolatedAsyncioTestCase):

    async def test_tabular_classification(self):
        dataset_path = load_titanic_dataset()
        # setup request as it is coming in from controller
        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':tabular_classification'
        req.configuration.target = "survived"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "age": 2,
                "sex": 1,
                "survived": 2 ,
            },
             "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "thousands_seperator": ",",
                "datetime_format": "",
                "encoding": ""
            },
            "schema": {
                "survived": {
                    "datatype_detected": ":boolean",
                    "role_selected": ":target"
                }
            }
        })

        # start training
        adapter_manager = EvalMLAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "evalml-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' does not exist")

        # clean up
        shutil.rmtree(out_dir)
    
    async def test_tabular_regression(self):
        dataset_path = load_titanic_dataset()
        # setup request as it is coming in from controller
        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':tabular_regression'
        req.configuration.target = "survived"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "age": 2,
                "sex": 1,
                "survived": 2 ,
            },
             "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "thousands_seperator": ",",
                "datetime_format": "",
                "encoding": ""
            },
            "schema": {
                "survived": {
                    "datatype_detected": ":integer",
                    "role_selected": ":target"
                }
            }
        })

        # start training
        adapter_manager = EvalMLAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "evalml-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' does not exist")

        # clean up
        shutil.rmtree(out_dir)

        
if __name__ == '__main__':
    unittest.main()

