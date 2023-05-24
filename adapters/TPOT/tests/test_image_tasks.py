import json
import os
import shutil
import unittest
import uuid

from AdapterBGRPC import StartAutoMlRequest
from TPOTAdapterManager import TPOTAdapterManager
from sklearn.datasets import load_digits
from PIL import Image
from sklearn.model_selection import train_test_split
import numpy as np


def load_digits_image_dataset() -> str:
    """download digits dataset, return dataset directory path"""
    # downloads and saves images of hand-drawn images in the following format:
    # mnist
    # ├── test
    # │   └── 7  <-------------- digit drawn in image ( y )
    # │       └── 0.jpeg  <----- image of a hand-drawn image ( X ), filename is random int
    # └── train
    #     ├── 0
    #     │   ├── 1.jpeg
    #     │   └── ...
    #     ├── 1
    #     │   ├── 14.jpeg
    #     │   └── ...
    #     ├── ...
    #     └── 9
    #         ├── 19.jpeg
    #         └── ...

    def save_subset(dir_name, x , y):
        os.makedirs(dir_name, exist_ok=True)
        for i in range(10):  # 10 possible targets
            if not os.path.exists(os.path.join(dir_name, str(i))):
                os.makedirs(os.path.join(dir_name, str(i)))


        # convert images
        for i in range(x.shape[0]):
            target = str(y[i])
            image_array = x[i].reshape(8, 8)
            image = Image.fromarray(np.uint8(image_array * 255))
            image_path = os.path.join(dir_name, target, f'{i}.jpeg')
            image.save(image_path)


    # build subset paths
    dataset_folder = os.path.join("tests", "datasets", "digits")
    train_dir = os.path.join(dataset_folder, "train")
    test_dir = os.path.join(dataset_folder, "test")

    digits = load_digits()
    x_train, x_test, y_train, y_test = train_test_split(digits.data, digits.target,
                                                    train_size=0.75, test_size=0.25)
    save_subset(train_dir, x_train[:10], y_train[:10])
    save_subset(test_dir, x_test[:1], y_test[:1])

    return dataset_folder



class TPOTImageTaskTest(unittest.TestCase):

    # def setUp(self):
    #     # NOTE: we are running the test in the repos root directory.
    #     #       the application is expected to start inside the adapter solution,
    #     #       so we need to change working directories
    #     tpot_dir = os.path.join("adapters", "TPOT")
    #     os.chdir(tpot_dir)

    # def tearDown(self):
    #     # reset the working directory before finishing this test
    #     os.chdir(os.path.join("..", ".."))

    def test_image_classification(self):

        dataset_path = load_digits_image_dataset()


        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':image_classification'
        req.configuration.target = "target"
        req.configuration.runtime_limit = 10
        req.configuration.metric = ':accuracy'
        req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {},
            "file_configuration": {},
            "schema": {
            },
            "multi_fidelity_level": 0
        })

        adapter_manager = TPOTAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "tpot-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' exist")

        # clean up
        shutil.rmtree(out_dir)

if __name__ == '__main__':
    unittest.main()
