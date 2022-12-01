import shutil
from os.path import dirname
from pathlib import Path
from ControllerBGRPC import CreateDatasetRequest, CreateDatasetResponse
from Container import *
from AdapterBGRPC import *
from dependency_injector.wiring import inject, Provide
from unittest import IsolatedAsyncioTestCase
import unittest

USER_ID = "12-34-56-78"

class TestDataUpload(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        
        base_path = dirname(__file__)
        self.test_data_path = f"{base_path}\\datasets"#DATASET_NAME
        base_path = os.path.normpath(os.path.join(base_path, '..'))
        base_path = f"{base_path}\\app-data\\datasets"
        self.__upload_file_path = f"{base_path}\\{USER_ID}\\uploads"#+DATASET_NAME
        Path(self.__upload_file_path).mkdir(parents=True, exist_ok=True)

        mongo = MongoDbClient(server_url=None)
        self.__data_storage = DataStorage(data_storage_dir=base_path,mongo_db=mongo)
        self.__dataset_manager = DatasetManager(self.__data_storage, ThreadLock())


    async def test_tabular_upload(self):
        tabular_test_data_dir = f"{self.test_data_path}\\tabular\\"
        for file in os.listdir(os.fsencode(tabular_test_data_dir)):
            filename = os.fsdecode(file)
            shutil.copy(tabular_test_data_dir+filename, self.__upload_file_path)
            create_request = CreateDatasetRequest()
            create_request.user_id=USER_ID
            create_request.file_name= filename
            create_request.dataset_name= filename
            create_request.dataset_type=":tabular"
            create_respone = self.__dataset_manager.create_dataset(create_request)
            self.assertIsInstance(create_respone,CreateDatasetResponse)
            
    async def test_imgae_upload(self):
        image_test_data_dir = f"{self.test_data_path}\\image\\"
        for file in os.listdir(os.fsencode(image_test_data_dir)):
            filename = os.fsdecode(file)
            shutil.copy(image_test_data_dir+filename, self.__upload_file_path)
            create_request = CreateDatasetRequest()
            create_request.user_id=USER_ID
            create_request.file_name= filename
            create_request.dataset_name= filename
            create_request.dataset_type=":image"
            create_respone = self.__dataset_manager.create_dataset(create_request)
            self.assertIsInstance(create_respone,CreateDatasetResponse)


    def tearDown(self):
       shutil.rmtree(dirname(self.__upload_file_path))
       

if __name__ == '__main__':
    unittest.main()