import json
import os
import shutil
import unittest
from unittest import IsolatedAsyncioTestCase
import uuid

import pandas as pd
from GAMAAdapterManager import GAMAAdapterManager
from Container import *
from AdapterBGRPC import *

from sklearn.datasets import load_iris

def load_iris_dataset() -> str:
    """download iris dataset and build csv file, return csv path"""

    #load dataset
    iris = load_iris()
    train_data = pd.DataFrame(iris['data'], columns=iris['feature_names'])
    train_data['target'] = iris['target']
    # save dataset to file
    os.makedirs(os.path.join("tests", "datasets"), exist_ok=True)
    file_path = os.path.join("tests", "datasets", "iris.csv")

    train_data.to_csv(file_path, index=False)
    return file_path
def load_titanic_dataset():
    """download titanic dataset
    Returns:
        path of reduced dataset csv
    """
    cache_dir = os.path.join("tests", "datasets")
    os.makedirs(cache_dir, exist_ok=True)
    titanic: pd.DataFrame = pd.read_csv(filepath_or_buffer="https://storage.googleapis.com/tf-datasets/titanic/train.csv",)

    # drop other columns for simplicity
    titanic = titanic[["age", "sex", "survived","n_siblings_spouses","alone"]]

    dataset_path = os.path.join(cache_dir, "titanic.csv")
    with open(dataset_path, "w+") as outfp:
        pd.DataFrame.to_csv(titanic, outfp, index=False)

    return dataset_path


class GAMATabularTaskTest(unittest.TestCase):

    def test_tabular_classification(self):
        dataset_path = load_iris_dataset()
        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':tabular_classification'
        req.configuration.target = "target"
        req.configuration.runtime_limit = 3
        #req.configuration.metric = ':accuracy'
        #req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "target": ":integer",
                "sepal length (cm)": ":float",
                "sepal width (cm)": ":float",
                "petal length (cm)": ":float",
                "petal width (cm)": ":float"

            },
            "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "thousands_seperator": ",",
                "datetime_format": "",
                "encoding": "utf-8"
            },
            "schema": {
                "target": {
                    "datatype_detected": ":int",
                    "role_selected": ":target"
                }
            },
            "multi_fidelity_level": 0
        })

        # start training
        adapter_manager = GAMAAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "gama-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' does not exist")

        # clean up
        shutil.rmtree(out_dir)

    def test_tabular_regression(self):
        dataset_path = load_iris_dataset()


        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':tabular_regression'
        req.configuration.target = "target"
        req.configuration.runtime_limit = 3
        #req.configuration.metric = ':accuracy'
        #req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "target": ":integer",
                "sepal length (cm)": ":float",
                "sepal width (cm)": ":float",
                "petal length (cm)": ":float",
                "petal width (cm)": ":float"

            },
            "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "thousands_seperator": ",",
                "datetime_format": "",
                "encoding": "utf-8"
            },
            "schema": {
                "target": {
                    "datatype_detected": ":int",
                    "role_selected": ":target"
                }
            },
            "multi_fidelity_level": 0
        })

        # start training
        adapter_manager = GAMAAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "gama-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' does not exist")

        # clean up
        shutil.rmtree(out_dir)
    

        
if __name__ == '__main__':
    unittest.main()

