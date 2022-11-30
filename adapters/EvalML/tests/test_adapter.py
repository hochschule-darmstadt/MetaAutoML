import sys
import os
from pathlib import Path
base_path = sys.path[0]
base_path = base_path.replace("\\tests", "")
sys.path.insert(0,base_path)
sys.path.insert(0, str(os.path.join(base_path, "AutoMLs")))
sys.path.insert(0, str(os.path.join(base_path, "dependency-injection")))
base_path = base_path.replace("\\EvalML", "")
sys.path.insert(0, str(os.path.join(base_path, "Utils/Utils")))
sys.path.insert(0, str(os.path.join(base_path, "Utils/AutoMLs")))
sys.path.insert(0, str(os.path.join(base_path, "GRPC/Adapter")))
from EvalMLAdapter import EvalMlAdapterManager
from Container import *
from AdapterBGRPC import *
from dependency_injector.wiring import inject, Provide
from unittest import IsolatedAsyncioTestCase
import unittest
events = []
TRAINING_ID = '63650604550f952c84d49b06'
DATASET_ID = '63538f02a8499d239605e4c3'
USER_ID = 'e1d36b1b-bb75-4f16-a631-d93bdb31e9c7'

class TestAdapter(IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.__session_id = ""
        self.__adapter_manager = EvalMlAdapterManager()
    
    @inject
    async def test_start_automl_process(self):
        start_automl_request = StartAutoMlRequest()

        self.__session_id = uuid.uuid4()

        start_automl_request.training_id = TRAINING_ID
        start_automl_request.dataset_id = DATASET_ID
        start_automl_request.user_id = USER_ID
        start_automl_request.dataset_path = 'C:\\Users\\Hung\\Personal\\Sem1\\MetaAutoML\\controller\\app-data/datasets\\'+start_automl_request.user_id+'\\'+start_automl_request.dataset_id+'\\titanic_train.csv'
        start_automl_request.configuration.task = ':tabular_classification'
        start_automl_request.configuration.target = 'Survived'
        start_automl_request.configuration.runtime_limit = 3
        start_automl_request.configuration.metric = ':accuracy'
        start_automl_request.dataset_configuration = '{"column_datatypes": {"PassengerId": 2, "Survived": 5, "Pclass": 2, "Name": 1, "Sex": 1, "Age": 3, "SibSp": 2, "Parch": 2, "Ticket": 1, "Fare": 3, "Cabin": 1, "Embarked": 1}, "file_configuration": {"use_header": true, "start_row": 1, "delimiter": "comma", "escape_character": "\\\\", "decimal_character": "."}}'
        
        self.__adapter_manager.start_auto_ml(start_automl_request, self.__session_id)
        self.__adapter_manager.start()
        self.__adapter_manager.join()
        self.assertEqual(self.__adapter_manager.get_start_auto_ml_request(), start_automl_request)
        path_to_model = 'C:\\Users\\Hung\\Personal\\Sem1\\MetaAutoML\\adapters\\AutoKeras\\app-data\\training\\'+start_automl_request.user_id+'\\'+start_automl_request.dataset_id+'\\'+start_automl_request.training_id+'\\export\\keras-export.zip'
        # check if model exists
        self.assertEqual(True, Path(path_to_model).is_file())
        #self.assertEqual(True, False)
        # delete exported model 
        export_model_to_be_deleted = 'C:\\Users\\Hung\\Personal\\Sem1\\MetaAutoML\\adapters\\AutoKeras\\app-data\\training\\'+start_automl_request.user_id+'\\'+start_automl_request.dataset_id+'\\'+start_automl_request.training_id
        shutil.rmtree(export_model_to_be_deleted)

    def tearDown(self):
        pass
if __name__ == '__main__':
    unittest.main()