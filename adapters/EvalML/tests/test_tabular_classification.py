import sys
import os

base_path = sys.path[0]
base_path = base_path.replace("\\tests", "")
sys.path.insert(0,base_path)
sys.path.insert(0, str(os.path.join(base_path, "AutoMLs")))
sys.path.insert(0, str(os.path.join(base_path, "dependency-injection")))
base_path = base_path.replace("\\EvalML", "")
sys.path.insert(0, str(os.path.join(base_path, "Utils/Utils")))
sys.path.insert(0, str(os.path.join(base_path, "Utils/AutoMLs")))
sys.path.insert(0, str(os.path.join(base_path, "GRPC/Adapter")))

from EvalMLAdapterManager import EvalMlAdapterManager
from Container import *
from AdapterBGRPC import *
from unittest import IsolatedAsyncioTestCase
import unittest

class TestAdapter(IsolatedAsyncioTestCase):
    
    async def test_start_automl_process(self):
        start_automl_request = StartAutoMlRequest()
        start_automl_request.training_id = "test"
        start_automl_request.dataset_id = "test"
        start_automl_request.user_id = "test"
        start_automl_request.dataset_path = "tests/datasets/10_modulo.csv"
        start_automl_request.configuration.task = ':tabular_classification'
        start_automl_request.configuration.target = 'Even'
        start_automl_request.configuration.runtime_limit = 3
        start_automl_request.configuration.metric = ':accuracy'
        start_automl_request.dataset_configuration = json.dumps({
            "column_datatypes": {
                "Number": 2, 
                "Even": 5
            }, 
            "file_configuration": {
                "use_header": True, 
                "start_row": 1, 
                "delimiter": "comma", 
                "escape_character": "\\", 
                "decimal_character": "." 
            }
        })

        session_id = uuid.uuid4()
        adapter_manager = EvalMlAdapterManager()
        adapter_manager.start_auto_ml(start_automl_request, session_id)
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training", start_automl_request.user_id, start_automl_request.dataset_id, start_automl_request.training_id)
        path_to_model = os.path.join(out_dir, "export", "evalml-export.zip")
        self.assertTrue(os.path.exists(path_to_model))
        
        # clean up
        shutil.rmtree(out_dir)
        
if __name__ == '__main__':
    unittest.main()
