import json
import shutil
import sys
import os
import uuid

base_path = sys.path[0]
base_path = base_path.replace("\\tests", "")
sys.path.insert(0,base_path)
sys.path.insert(0, str(os.path.join(base_path, "AutoMLs")))
sys.path.insert(0, str(os.path.join(base_path, "dependency-injection")))
base_path = base_path.replace("\\AutoKeras", "")
sys.path.insert(0, str(os.path.join(base_path, "Utils/Utils")))
sys.path.insert(0, str(os.path.join(base_path, "Utils/AutoMLs")))
sys.path.insert(0, str(os.path.join(base_path, "GRPC/Adapter")))

from AutoKerasAdapterManager import AutoKerasAdapterManager
from Container import *
from AdapterBGRPC import *
from unittest import IsolatedAsyncioTestCase
import unittest

class TestAdapter(IsolatedAsyncioTestCase):

    async def test_start_automl_process(self):

        autokeras_dir = "adapters/AutoKeras"
        os.chdir(autokeras_dir)

        start_automl_request = StartAutoMlRequest()
        start_automl_request.training_id = "test"
        start_automl_request.dataset_id = "test"
        start_automl_request.user_id = "test"
        start_automl_request.dataset_path = "tests/datasets/pens"
        start_automl_request.file_location = "tests/datasets/pens"
        start_automl_request.configuration.task = ':image_classification'
        start_automl_request.configuration.target = 'Even'
        start_automl_request.configuration.runtime_limit = 1
        start_automl_request.configuration.metric = ':accuracy'
        start_automl_request.dataset_configuration = json.dumps({ })

        session_id = uuid.uuid4()
        adapter_manager = AutoKerasAdapterManager()
        adapter_manager.start_auto_ml(start_automl_request, session_id)
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training", start_automl_request.user_id, start_automl_request.dataset_id, start_automl_request.training_id)
        path_to_model = os.path.join(out_dir, "export", "keras-export.zip")
        self.assertTrue(os.path.exists(path_to_model))
        
        # clean up
        shutil.rmtree(out_dir)
        
if __name__ == '__main__':
    unittest.main()
