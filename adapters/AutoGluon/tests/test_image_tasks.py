import json
import os
import shutil
import unittest
import uuid

from PIL import Image
from AdapterBGRPC import StartAutoMlRequest
from AutoGluonAdapterManager import AutoGluonAdapterManager
from autogluon.multimodal.utils.misc import shopee_dataset


def load_math_dataset() -> str:
    """download math dataset and build csv file, return csv path"""

    def save_subset(dir_name, x, y):
        for i, (img, digit) in enumerate(zip(x, y)):

            # create folder for each digit
            folder = os.path.join(dir_name, str(digit))
            os.makedirs(folder, exist_ok=True)

            # save image to file
            file_path = os.path.join(folder, f"{i}.jpeg")
            img = Image.fromarray(img)
            img = img.convert("RGB")
            img.save(file_path)
    #load dataset
    dataset_folder = os.path.join("tests", "datasets", "ag_automm_tutorial_imgcls")
    train_data_byte, test_data_byte = shopee_dataset(dataset_folder, is_bytearray=True)

    file_path = os.path.join("tests", "datasets", "ag_automm_tutorial_imgcls", "shopee")
    return file_path

class AutoGluonTextTaskTest(unittest.TestCase):

    # def setUp(self):
    #     # NOTE: we are running the test in the repos root directory.
    #     #       the application is expected to start inside the adapter solution,
    #     #       so we need to change working directories
    #     autogluon_dir = os.path.join("adapters", "AutoGluon")
    #     os.chdir(autogluon_dir)

    # def tearDown(self):
    #     # reset the working directory before finishing this test
    #     os.chdir(os.path.join("..", ".."))

    def test_text_classification(self):

        dataset_path = load_math_dataset()


        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':image_classification'
        req.configuration.target = "label"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {},
            "file_configuration": {},
            "schema": {
            },
            "multi_fidelity_level": 0
        })

        adapter_manager = AutoGluonAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "gluon-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' exist")

        # clean up
        shutil.rmtree(out_dir)

if __name__ == '__main__':
    unittest.main()
