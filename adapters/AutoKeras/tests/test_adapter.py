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
from dependency_injector.wiring import inject, Provide
from unittest import IsolatedAsyncioTestCase
import unittest
events = []

class TestAdapter(IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.__session_id = ""
        self.__adapter_manager = AutoKerasAdapterManager()
    
    @inject
    async def test_start_automl_process(self):
        start_automl_request = StartAutoMlRequest()

        self.__session_id = uuid.uuid4()

        start_automl_request.training_id = '63650604550f952c84d49b06'
        start_automl_request.dataset_id = '636103218914d435d27924d6'
        start_automl_request.user_id = '6d61d9eb-722d-4c94-b4df-ed1cbfebeb35'
        start_automl_request.dataset_path = 'C:\\Users\\alex\\Desktop\\MetaAutoML\\controller\\app-data/datasets\\6d61d9eb-722d-4c94-b4df-ed1cbfebeb35\\636103218914d435d27924d6\\titanic_train.csv'
        start_automl_request.configuration.task = ':tabular_classification'
        start_automl_request.configuration.target = 'Survived'
        start_automl_request.configuration.runtime_limit = 3
        start_automl_request.configuration.metric = ':accuracy'
        start_automl_request.dataset_configuration = '{"column_datatypes": {"PassengerId": 2, "Survived": 5, "Pclass": 2, "Name": 1, "Sex": 1, "Age": 3, "SibSp": 2, "Parch": 2, "Ticket": 1, "Fare": 3, "Cabin": 1, "Embarked": 1}, "file_configuration": {"use_header": true, "start_row": 1, "delimiter": "comma", "escape_character": "\\\\", "decimal_character": "."}}'
        
        self.__adapter_manager.start_auto_ml(start_automl_request, self.__session_id)
        self.__adapter_manager.start()
        self.assertNotEqual(len("asds"), 0)

    def tearDown(self):
        pass
if __name__ == '__main__':
    unittest.main()