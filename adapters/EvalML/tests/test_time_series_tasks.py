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

from evalml.demos import load_weather



def load_dataset():
    X, y = load_weather()
    X_new = X.merge(y,left_index=True, right_index=True)
    #X_new['DateTime'] = X_new['Date']
    cache_dir = os.path.join("tests", "datasets")
    os.makedirs(cache_dir, exist_ok=True)
    #print(X_new['Temp'])
    dataset_path = os.path.join(cache_dir, "test.csv")
    with open(dataset_path, "w+") as outfp:
        pd.DataFrame.to_csv(X_new, outfp, index=False)

    return dataset_path

class TestAdapter(IsolatedAsyncioTestCase):
    async def test_tabular_classification(self):
        dataset_path = load_dataset()
        # setup request as it is coming in from controller
        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':time_series_forecasting'
        req.configuration.target = "Temp"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.dataset_configuration = json.dumps({
            "multi_fidelity_level": 0,
            "schema": {
                "Date":{
                    'datatype_detected':':datetime',
                    'datatype_compatible':[':datetime'],
                    'roles_compatible':[':index'],
                    'role_selected':':index',
                },
                "Temp":{
                    'datatype_detected':':float',
                    'datatype_compatible':[':float'],
                    'roles_compatible':[':target'],
                    'role_selected':':target',
                },
            },
            "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "encoding": "ascii",
                "thousands_seperator": "",
                "datetime_format": '%Y-%m-%d'
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
