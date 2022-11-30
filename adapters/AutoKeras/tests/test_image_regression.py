import json
import sys
import os
import uuid
import AdapterUtils
from AutoKerasAdapter import AutoKerasAdapter
from AutoKerasAdapterManager import AutoKerasAdapterManager
# from AutoKerasAdapter import AutoKerasAdapter

# base_path = sys.path[0]
# base_path = base_path.replace("\\tests", "")
# sys.path.insert(0,base_path)
# sys.path.insert(0, str(os.path.join(base_path, "AutoMLs")))
# sys.path.insert(0, str(os.path.join(base_path, "dependency-injection")))
# base_path = base_path.replace("\\AutoKeras", "")
# sys.path.insert(0, str(os.path.join(base_path, "Utils/Utils")))
# sys.path.insert(0, str(os.path.join(base_path, "Utils/AutoMLs")))
# sys.path.insert(0, str(os.path.join(base_path, "GRPC/Adapter")))

# from AutoKerasAdapterManager import AutoKerasAdapterManager
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
        start_automl_request.dataset_path = "tests/datasets/facials"
        start_automl_request.file_location = "tests/datasets/facials"
        start_automl_request.configuration.task = ':image_regression'
        start_automl_request.configuration.target = 'Even'
        start_automl_request.configuration.runtime_limit = 1
        start_automl_request.configuration.metric = ':accuracy'
        start_automl_request.dataset_configuration = json.dumps({ })

        session_id = uuid.uuid4()
        adapter_manager = AutoKerasAdapterManager()
        adapter_manager.start_auto_ml(start_automl_request, session_id)
        adapter_manager.start()
        adapter_manager.join()
        # config = {
        #     "training_id": "test", 
        #     "dataset_id": "test", 
        #     "user_id": "test", 
        #     "dataset_path": "tests/datasets/facials", 
        #     "configuration": {
        #         "task": ":image_regression", 
        #         "runtime_limit": 3,
        #         "metric": ":accuracy"
        #     },
        #     "dataset_configuration": "{}", 
        #     "file_location": "tests/datasets/facials", 
        #     "job_folder_location": "app-data/training/test/test/test/job", 
        #     "model_folder_location": "app-data/training/test/test/test/model", 
        #     "export_folder_location": "app-data/training/test/test/test/export", 
        #     "result_folder_location": "app-data/training/test/test/test/result", 
        #     "controller_export_folder_location": "app-data/training/AutoKeras/test/test/test/export"
        # }
        # AdapterUtils.setup_run_environment(config, "AutoKeras")
        # adapter = AutoKerasAdapter(config)
        # adapter.start()

        # check if model archive exists
        # path_to_model = os.path.join(config["export_folder_location"], "keras-export.zip")
        # self.assertTrue(os.path.exists(path_to_model))
        
        # # clean up
        # traning_dir = os.path.dirname(config["export_folder_location"])
        # shutil.rmtree(traning_dir)
        
if __name__ == "__main__":
    unittest.main()
