import json
import os
import shutil
import unittest
import uuid

from AdapterBGRPC import StartAutoMlRequest
from FLAMLAdapterManager import FLAMLAdapterManager
import pandas as pd
from datasets import load_dataset


def load_glue_dataset() -> str:
    """download glue dataset and build csv file, return csv path"""

    train_data = load_dataset("glue", "mrpc", split="train").to_pandas()
    # save dataset to file
    os.makedirs(os.path.join("tests", "datasets"), exist_ok=True)
    file_path = os.path.join("tests", "datasets", "glue.csv")

    train_data.to_csv(file_path, index=False)
    return file_path

class FLAMLTabularTaskTest(unittest.TestCase):

    def test_text_classification(self):

        dataset_path = load_glue_dataset()


        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':text_classification'
        req.configuration.target = "label"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "label": ":integer",
                "sentence1":":string",
                "sentence2":":string",
                "idx":":integer"

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
                "label": {
                    "datatype_detected": ":int",
                    "role_selected": ":target"
                },
                "sentence1": {
                    "datatype_detected": ":string",
                    "role_selected": ":none"
                },
                "sentence2": {
                    "datatype_detected": ":string",
                    "role_selected": ":none"
                },
                "idx": {
                    "datatype_detected": ":int",
                    "role_selected": ":index"
                }
            },
            "multi_fidelity_level": 0
        })

        adapter_manager = FLAMLAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "flaml-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' exist")

        # clean up
        shutil.rmtree(out_dir)

if __name__ == '__main__':
    unittest.main()
