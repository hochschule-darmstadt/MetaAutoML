import json
import os
import shutil
import unittest
import uuid

from autogluon.core.utils.loaders import load_pd
from AdapterBGRPC import StartAutoMlRequest
from AutoGluonAdapterManager import AutoGluonAdapterManager
from autogluon.core.utils.loaders import load_pd
import pandas as pd
from sklearn.datasets import load_files


def load_sentiment_dataset() -> str:
    """download sentiment dataset and build csv file, return csv path"""

    #load dataset
    #train_data = load_pd.load('https://autogluon-text.s3-accelerate.amazonaws.com/glue/sst/train.parquet')

    # save dataset to file
    #os.makedirs(os.path.join("tests", "datasets"), exist_ok=True)
    file_path = os.path.join("tests", "datasets", "SPAM_HAM.csv")

    #train_data.to_csv(file_path, index=False)
    return file_path

def load_named_entity_dataset() -> str:
    """download named entity dataset and build csv file, return csv apath"""

    #load dataset
    train_data = load_pd.load('https://automl-mm-bench.s3.amazonaws.com/ner/mit-movies/train_v2.csv')

    #save dataset to file
    os.makedirs(os.path.join("tests", "datasets"), exist_ok=True)
    file_path = os.path.join("tests", "datasets", "mit_movies.csv")

    train_data.to_csv(file_path, index=False)
    return file_path

class AutoGluonTextTaskTest(unittest.TestCase):

    def setUp(self):
        # NOTE: we are running the test in the repos root directory.
        #       the application is expected to start inside the adapter solution,
        #       so we need to change working directories
        autogluon_dir = os.path.join("adapters", "AutoGluon")
        os.chdir(autogluon_dir)

    def tearDown(self):
        # reset the working directory before finishing this test
        os.chdir(os.path.join("..", ".."))

    def test_text_classification(self):

        dataset_path = load_sentiment_dataset()

        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':text_classification'
        req.configuration.target = "Category"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "Message": ":string",
                "Category":":string"
            },
            "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "thousands_seperator": ",",
                "datetime_format": "",
                "encoding": "latin-1"
            },
            "schema": {
                "Category": {
                    "datatype_detected": ":string",
                    "role_selected": ":target"
                },
                "Message": {
                    "datatype_detected": ":string",
                    "role_selected": ":none"
                }
            },
            "multi_fidelity_level": 0
        })

        adapter_manager = AutoGluonAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "gluon-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' exist")

        # clean up
        shutil.rmtree(out_dir)

    def test_text_named_entity_recognition(self):

        dataset_path = load_named_entity_dataset()

        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':named_entity_recognition'
        req.configuration.target = "entity_annotations"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':overall_accuracy'
        req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "text_snippet": ":string",
                "entity_annotations":":object"
            },
            "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "thousands_seperator": ",",
                "datetime_format": "",
                "encoding": "latin-1"
            },
            "schema": {
                "entity_annotations": {
                    "datatype_detected": ":obejct",
                    "role_selected": ":target"
                },
                "text_snippet": {
                    "datatype_detected": ":string",
                    "role_selected": ":none"
                }
            },
            "multi_fidelity_level": 0
        })

        adapter_manager = AutoGluonAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "gluon-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' exist")

        # clean up
        shutil.rmtree(out_dir)


if __name__ == '__main__':
    unittest.main()
