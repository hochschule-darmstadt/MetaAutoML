import json
import shutil
import os
import uuid
import unittest

from AutoKerasAdapterManager import AutoKerasAdapterManager
from unittest import IsolatedAsyncioTestCase
from AdapterBGRPC import StartAutoMlRequest

import sklearn.datasets
from pandas import DataFrame


class AutoKerasTabularRegressionTest(IsolatedAsyncioTestCase):

    def prepare_test_dataset():

        file_path = os.path.join("tests", "datasets", "diabetes.csv")
        if not os.path.exists(file_path):
            print("did not find dataset, will download")
            diabetes = sklearn.datasets.load_diabetes(
                as_frame=True, scaled=False)
            # drop columns that are not interesting
            diabetes: DataFrame = diabetes.frame[["age", "sex", "bmi"]]

            diabetes["age"] = diabetes["age"].astype("int")
            diabetes["sex"] = diabetes["sex"].astype("int")
            diabetes["bmi"] = diabetes["bmi"].astype("int")

            with open(file_path, "w+") as outfp:
                DataFrame.to_csv(diabetes, outfp)

        return file_path

    def test_start_automl_process(self):

        # NOTE: we are running the test in the root directory.
        #       the application is expected to start inside the adapter solution,
        #       so we need to change working directories
        autokeras_dir = "adapters/AutoKeras"
        os.chdir(autokeras_dir)

        dataset_path = AutoKerasTabularRegressionTest.prepare_test_dataset()

        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ":tabular_regression"
        req.configuration.target = "bmi"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ":accuracy"
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                # all integers
                "age": 2,
                "sex": 2,
                "bmi": 2
            },
            "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": "."
            }
        })

        adapter_manager = AutoKerasAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "keras-export.zip")
        self.assertTrue(os.path.exists(path_to_model))

        # clean up
        shutil.rmtree(out_dir)


if __name__ == "__main__":
    unittest.main()
