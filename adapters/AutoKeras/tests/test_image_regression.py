import json
import shutil
import os
import uuid
import unittest
import numpy as np
import sklearn.datasets
from PIL import Image

from AdapterBGRPC import StartAutoMlRequest
from AutoKerasAdapterManager import AutoKerasAdapterManager


class TestAdapter(unittest.IsolatedAsyncioTestCase):

    def prepare_test_dataset():
        # load image dataset with hand-drawn digits
        #   X = numpy array with numbers from 0-16 --> needs scaling to 0-255
        #   y = integer indicating the number in the picture
        X_digits, y_digits = sklearn.datasets.load_digits(return_X_y=True)
        # take only a small subset for this test
        X_y = list(zip(X_digits, y_digits))[:20]

        dataset_folder = os.path.join("tests", "datasets", "digits")

        for i, (img, digit) in enumerate(X_y):

            # reshape array into 8x8 matrix and
            img = np.reshape(img, (8, 8))
            # scale each pixel to 0-255
            img = img * 16

            # 25% of images are test data
            ftype = "test" if i % 4 == 0 else "train"

            # create folder and build image path
            folder = os.path.join(dataset_folder, ftype, str(digit))
            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, f"{i}.jpeg")

            # save image to file
            img = Image.fromarray(img)
            img = img.convert("RGB")
            img.save(file_path)

        return dataset_folder

    async def test_start_automl_process(self):

        # NOTE: we are running the test in the root directory.
        #       the application is expected to start inside the adapter solution,
        #       so we need to change working directories
        autokeras_dir = "adapters/AutoKeras"
        os.chdir(autokeras_dir)

        dataset_path = TestAdapter.prepare_test_dataset()

        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':image_regression'
        req.configuration.target = 'Even'
        req.configuration.runtime_limit = 1
        req.configuration.metric = ':accuracy'
        req.dataset_configuration = json.dumps({})

        session_id = uuid.uuid4()
        adapter_manager = AutoKerasAdapterManager()
        adapter_manager.start_auto_ml(req, session_id)
        adapter_manager.start()
        adapter_manager.join()

        # check if model archive exists
        out_dir = os.path.join("app-data", "training",
                               req.user_id, req.dataset_id, req.training_id)
        path_to_model = os.path.join(out_dir, "export", "keras-export.zip")
        self.assertTrue(os.path.exists(path_to_model))

        # clean up
        shutil.rmtree(out_dir)


if __name__ == "__main__":
    unittest.main()
