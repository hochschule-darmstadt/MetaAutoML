import json
import os
import shutil
import unittest
import uuid

from AdapterBGRPC import StartAutoMlRequest
from AutoKerasAdapterManager import AutoKerasAdapterManager
from keras.datasets import mnist
from PIL import Image


def load_mnist_image_dataset() -> str:
    """download mnist dataset, return dataset directory path"""
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

    # build subset paths
    dataset_folder = os.path.join("tests", "datasets", "mnist")
    train_dir = os.path.join(dataset_folder, "train")
    test_dir = os.path.join(dataset_folder, "test")

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    # take only a small subset for this test
    # NOTE: train dataset cannot be too small, otherwise Keras will complain
    save_subset(train_dir, x_train[:100], y_train[:100])
    save_subset(test_dir, x_test[:1], y_test[:1])

    return dataset_folder


class AutoKerasImageTaskTest(unittest.TestCase):

    def setUp(self):
        # NOTE: we are running the test in the reposroot directory.
        #       the application is expected to start inside the adapter solution,
        #       so we need to change working directories
        autokeras_dir = os.path.join("adapters", "AutoKeras")
        os.chdir(autokeras_dir)

    def tearDown(self):
        # reset the working directory before finishing this test
        os.chdir(os.path.join("..", ".."))

    def test_image_regression(self):

        dataset_path = load_mnist_image_dataset()

        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':image_regression'
        # we do not need a target, it will be ignored,
        #   the default is None, which will raise an error
        req.configuration.target = ""
        req.configuration.runtime_limit = 1
        req.configuration.metric = ':accuracy'
        # we do not need a dataset configuration
        req.dataset_configuration = json.dumps({})

        adapter_manager = AutoKerasAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "keras-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' does not exist")

        # clean up
        shutil.rmtree(out_dir)

    def test_image_classification(self):

        dataset_path = load_mnist_image_dataset()

        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':image_classification'
        # we do not need a target, it will be ignored,
        #   the default is None, which will raise an error
        req.configuration.target = ""
        req.configuration.runtime_limit = 1
        req.configuration.metric = ':accuracy'
        # we do not need a dataset configuration
        req.dataset_configuration = json.dumps({})

        adapter_manager = AutoKerasAdapterManager()
        adapter_manager.start_auto_ml(req, uuid.uuid4())
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "keras-export.zip")
        self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' does not exist")

        # clean up
        shutil.rmtree(out_dir)


if __name__ == '__main__':
    unittest.main()
