import sys
import os

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

class AutoKerasTabularRegressionTest(IsolatedAsyncioTestCase):
    
    async def test_start_automl_process(self):
        request = StartAutoMlRequest()
        request.training_id = "test"
        request.dataset_id = "test"
        request.user_id = "test"
        request.dataset_path = "tests/datasets/even_numbers.csv"
        request.configuration.task = ":tabular_regression"
        request.configuration.target = "Even"
        request.configuration.runtime_limit = 3
        request.configuration.metric = ":accuracy"
        request.dataset_configuration = json.dumps({
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
        adapter_manager = AutoKerasAdapterManager()
        adapter_manager.start_auto_ml(request, session_id)
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training", request.user_id, request.dataset_id, request.training_id)
        path_to_model = os.path.join(out_dir, "export", "keras-export.zip")
        self.assertTrue(os.path.exists(path_to_model))
        
        # clean up
        shutil.rmtree(out_dir)
        
if __name__ == "__main__":
    unittest.main()
