import shutil
from os.path import dirname
from pathlib import Path
from zipfile import ZipFile
from ControllerBGRPC import CreateDatasetRequest, CreateDatasetResponse
from Container import *
from AdapterBGRPC import *
from dependency_injector.wiring import inject, Provide
from unittest import IsolatedAsyncioTestCase
import unittest

from DataSetAnalysisManager import DataSetAnalysisManager

os.environ['KAGGLE_CONFIG_DIR'] = os.path.normpath(os.path.join(dirname(__file__), '..\\..\\auth'))
import kaggle

USER_ID = "12-34-56-78"
TABULAR_DATA_NAMES = ["titanic","house-prices-advanced-regression-techniques"]
IMAGE_DATA_NAMES = ["petfinder-pawpularity-score"]


class TestDataUpload(IsolatedAsyncioTestCase):
    """
    Test class dedicated to testing the upload of datasets.
    Args:
        IsolatedAsyncioTestCase (_type_): asynchronous test case
    """
    
    def setUp(self) -> None:
        """
        Sets up the test enviroment by getting needed file paths, downloading test data and initializing the DataStorage and DatasetManager.
        """
        base_path = dirname(__file__)
        self.__test_data_path = f"{base_path}\\datasets"#DATASET_NAME
        base_path = os.path.normpath(os.path.join(base_path, '..'))
        base_path = f"{base_path}\\app-data\\datasets"
        self.__upload_file_path = f"{base_path}\\{USER_ID}\\uploads"#+DATASET_NAME
        Path(self.__upload_file_path).mkdir(parents=True, exist_ok=True)

        tabularDir =  f"{self.__test_data_path}\\tabular\\"
        for competition in TABULAR_DATA_NAMES:
            try:
                kaggle.api.authenticate() 
                if (not os.path.exists(tabularDir + competition + ".csv")):
                    kaggle.api.competition_download_file(competition, "train.csv", path=tabularDir)
                    os.rename(tabularDir + "train.csv", tabularDir + competition + ".csv")
            except Exception as ex:
                print(f"Could not download {competition} dataset. Exception: {str(ex)}")

        imageDir =  f"{self.__test_data_path}\\image"
        for competition in IMAGE_DATA_NAMES:
            competitionDir = f"{imageDir}\\{competition}"
            try:
                if (not os.path.exists(competitionDir)):
                    kaggle.api.authenticate() 
                    kaggle.api.competition_download_files(competition, path=imageDir)          
            except Exception as ex:
                print(f"Could not download {competition} data. Exception: {str(ex)}")

        mongo = MongoDbClient(server_url=None)
        self.__data_storage = DataStorage(data_storage_dir=base_path,mongo_db=mongo)
        self.__dataset_manager = DatasetManager(self.__data_storage, ThreadLock())


    async def test_tabular_upload(self):
        """
        Tests 'creation' of tabular datasets within the system by invoking the create_dataset() method 
        of DatasetManager for each dataset within the tabular folder created in the setup
        """
        tabular_test_data_dir = f"{self.__test_data_path}\\tabular\\"
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
        """
        Tests 'creation' of image datasets within the system by invoking the create_dataset() method 
        of DatasetManager for each dataset within the image folder created in the setup
        """
        image_test_data_dir = f"{self.__test_data_path}\\image\\"
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