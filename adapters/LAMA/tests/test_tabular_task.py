import json
import os
import shutil
import unittest
import uuid

from AdapterBGRPC import StartAutoMlRequest
import pandas as pd
from LAMAAdapterManager import LAMAAdapterManager
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


class LAMATabularTaskTest(unittest.TestCase):

    # def setUp(self):
    #     # NOTE: we are running the test in the repos root directory.
    #     #       the application is expected to start inside the adapter solution,
    #     #       so we need to change working directories
    #     tpot_dir = os.path.join("adapters", "TPOT")
    #     os.chdir(tpot_dir)

    # def tearDown(self):
    #     # reset the working directory before finishing this test
    #     os.chdir(os.path.join("..", ".."))

    def test_tabulart_classification(self):

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

        adapter_manager = LAMAAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "lama-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' exist")

        # clean up
        shutil.rmtree(out_dir)


if __name__ == '__main__':
    unittest.main()