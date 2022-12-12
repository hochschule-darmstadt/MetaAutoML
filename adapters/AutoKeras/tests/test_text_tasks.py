import json
import os
import shutil
import unittest
import uuid

import keras
from AdapterBGRPC import StartAutoMlRequest
from AutoKerasAdapterManager import AutoKerasAdapterManager
from pandas import DataFrame
from sklearn.datasets import load_files

from controller.ControllerBGRPC import DataType


def load_aclImdb_dataset() -> str:
    """download aclImdb dataset and build csv file, return csv path"""

    cache_dir = os.path.join("tests", "datasets")
    os.makedirs(cache_dir, exist_ok=True)
    # do not extract the file for every test,
    #   the download will check the archive automatically
    needs_extract = not os.path.exists(os.path.join(cache_dir, "aclImdb"))

    dataset_path = keras.utils.get_file(
        fname="aclImdb.tar.gz",
        origin="http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz",
        extract=needs_extract,
        cache_dir=cache_dir,
        cache_subdir=""
    )

    # dataset_path as returned by keras includes the archives file extension
    #   but the function already extracts the data to a directory with the same name
    #   --> remove the file extension from the dataset_path
    dataset_dir = dataset_path[:-len(".tar.gz")]

    train_data = load_files(
        os.path.join(dataset_dir, "train"),
        shuffle=True
    )

    df = DataFrame.from_dict({
        # take only a small subset for this test
        # the text is in binary, so we need to decode it to utf-8 first
        "text": map(lambda x: x.decode("utf-8"), train_data.data[:60]),
        "target": train_data.target[:60]
    })

    # save dataset to file
    os.makedirs(os.path.join("tests", "datasets"), exist_ok=True)
    file_path = os.path.join("tests", "datasets", "aclImdb.csv")
    # do not include index column, Keras will complain otherwise:
    #   ValueError: Failed to convert a NumPy array to a Tensor (Unsupported object type int).
    df.to_csv(file_path, index=False)

    return file_path


class AutoKerasTextTaskTest(unittest.TestCase):

    def setUp(self):
        # NOTE: we are running the test in the repos root directory.
        #       the application is expected to start inside the adapter solution,
        #       so we need to change working directories
        autokeras_dir = os.path.join("adapters", "AutoKeras")
        os.chdir(autokeras_dir)

    def tearDown(self):
        # reset the working directory before starting this test
        os.chdir(os.path.join("..", ".."))

    def test_text_classification(self):

        dataset_path = load_aclImdb_dataset()

        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':text_classification'
        req.configuration.target = "target"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "text": DataType.DATATYPE_STRING,
                "target": DataType.DATATYPE_STRING
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

    def test_text_regression(self):

        dataset_path = load_aclImdb_dataset()

        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':text_regression'
        req.configuration.target = "target"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "text": DataType.DATATYPE_STRING,
                "target": DataType.DATATYPE_STRING
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


if __name__ == '__main__':
    unittest.main()
