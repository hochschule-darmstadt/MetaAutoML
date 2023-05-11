import json
import os
import shutil
import unittest
import uuid

import keras
import pandas as pd
from AdapterBGRPC import StartAutoMlRequest
from FLAMLAdapterManager import FLAMLAdapterManager
from ControllerBGRPC import DataType


def load_titanic_dataset():
    """download titanic dataset and return path of reduced dataset csv"""
    cache_dir = os.path.join("tests", "datasets")
    os.makedirs(cache_dir, exist_ok=True)
    dataset_path = keras.utils.get_file(
        fname="titanic_full.csv",
        origin="https://storage.googleapis.com/tf-datasets/titanic/train.csv",
        cache_dir=cache_dir,
        cache_subdir=""
    )

    titanic: pd.DataFrame = pd.read_csv(dataset_path)

    # drop other columns for simplicity
    titanic = titanic[["age", "sex", "survived"]]

    # dp not overwrite downloaded from the internet for caching
    dataset_path = os.path.join(os.path.dirname(dataset_path), "titanic.csv")
    with open(dataset_path, "w+") as outfp:
        pd.DataFrame.to_csv(titanic, outfp, index=False)

    return dataset_path

class FLAMLExplainerDashboardTest(unittest.TestCase):
    def test_tabular_classification(self):

        dataset_path = load_titanic_dataset()

        # setup request as it is coming in from controller
        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':tabular_classification'
        req.configuration.target = "survived"
        req.configuration.runtime_limit = 1
        req.configuration.metric = ':accuracy'
        req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "age": DataType.DATATYPE_INT,
                "sex": DataType.DATATYPE_STRING,
                "survived": DataType.DATATYPE_INT,
            },
            "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "thousands_seperator": ",",
                "datetime_format": "",
                "thousands_seperator": ",",
                "datetime_format": "",
                "encoding": ""
            },
            "schema": {
                "survived": {
                    "datatype_detected": ":boolean",
                    "role_selected": ":target"
                }
            },
            "multi_fidelity_level": 0
        })

        # start training
        adapter_manager = FLAMLAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "flaml-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' does not exist")
        path_to_dashboard = os.path.join(out_dir, "dashboard", "binary_dashboard.dill")
        self.assertTrue(os.path.exists(path_to_dashboard), f"path to dashboard: '{path_to_dashboard}' does not exist")

        # clean up
        shutil.rmtree(out_dir)

if __name__ == '__main__':
    unittest.main()