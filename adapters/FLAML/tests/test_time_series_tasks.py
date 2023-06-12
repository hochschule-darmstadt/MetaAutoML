import json
import os
import shutil
import unittest
import uuid

from AdapterBGRPC import StartAutoMlRequest
from FLAMLAdapterManager import FLAMLAdapterManager
import pandas as pd
import numpy as np


def create_dataset() -> str:
    """create dataset and build csv file, return csv path"""

    #create dataset
    X_train = np.arange("2014-01", "2022-01", dtype='datetime64[M]')
    y_train = np.random.random(size=84)
    train_data = pd.DataFrame({"time_series": X_train[:84], "target": y_train})
    # save dataset to file
    os.makedirs(os.path.join("tests", "datasets"), exist_ok=True)
    file_path = os.path.join("tests", "datasets", "example.csv")

    train_data.to_csv(file_path, index=False)
    return file_path

class FLAMLTimeSeriesTaskTest(unittest.TestCase):

    def test_time_series(self):

        dataset_path = create_dataset()


        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':time_series_forecasting'
        req.configuration.target = "target"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.configuration.parameters = {":metric": {"values": [":mean_squared_error"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "time_series": ":datetime",
                "target": ":float",

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
                    "datatype_detected": ":float",
                    "role_selected": ":target"
                },
                "time_series":{
                    'datatype_detected':':datetime',
                    'datatype_compatible':[':datetime'],
                    'roles_compatible':[':index'],
                    'role_selected':':index',
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
