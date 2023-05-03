import json
import os
import shutil
import unittest
import uuid

from autogluon.core.utils.loaders import load_pd
from AdapterBGRPC import StartAutoMlRequest
from AutoGluonAdapterManager import AutoGluonAdapterManager
from autogluon.tabular import TabularDataset
from autogluon.core.utils.loaders import load_pd
import pandas as pd
from sklearn.datasets import load_files


def load_math_dataset() -> str:
    """download math dataset and build csv file, return csv path"""

    #load dataset
    data_url = 'https://raw.githubusercontent.com/mli/ag-docs/main/knot_theory/'
    train_data = TabularDataset(f'{data_url}train.csv')
    # save dataset to file
    #os.makedirs(os.path.join("tests", "datasets"), exist_ok=True)
    file_path = os.path.join("tests", "datasets", "SPAM_HAM.csv")

    train_data.to_csv(file_path, index=False)
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

    # def test_text_classification(self):

    #     dataset_path = load_math_dataset()


    #     req = StartAutoMlRequest()
    #     req.training_id = "test"
    #     req.dataset_id = "test"
    #     req.user_id = "test"
    #     req.dataset_path = dataset_path
    #     req.configuration.task = ':tabular_classification'
    #     req.configuration.target = "signature"
    #     req.configuration.runtime_limit = 3
    #     req.configuration.metric = ':accuracy'
    #     req.configuration.parameters = {":metric": {"values": [":accuracy"]}}
    #     req.dataset_configuration = json.dumps({
    #         "column_datatypes": {
    #             "chern_simons": ":float",
    #             "signature":":int",
    #             "cusp_volume":":float",
    #             "hyperbolic_adjoint_torsion_degree":":int",
    #             "hyperbolic_torsion_degree":":int",
    #             "injectivity_radius":":float",
    #             "longitudinal_translation":":float",
    #             "meridinal_translation_imag":":float",
    #             "meridinal_translation_real":":float",
    #             "short_geodesic_imag_part":":float",
    #             "short_geodesic_real_part":":float",
    #             "Symmetry_0":":float",
    #             "Symmetry_D3":":float",
    #             "Symmetry_D4":":float",
    #             "Symmetry_D6":":float",
    #             "Symmetry_D8":":float",
    #             "Symmetry_Z/2 + Z/2	":":float",
    #             "volume":":float"

    #         },
    #         "file_configuration": {
    #             "use_header": True,
    #             "start_row": 1,
    #             "delimiter": "comma",
    #             "escape_character": "\\",
    #             "decimal_character": ".",
    #             "thousands_seperator": ",",
    #             "datetime_format": "",
    #             "encoding": "utf-8"
    #         },
    #         "schema": {
    #             "signature": {
    #                 "datatype_detected": ":int",
    #                 "role_selected": ":target"
    #             }
    #         },
    #         "multi_fidelity_level": 0
    #     })

    #     adapter_manager = AutoGluonAdapterManager()
    #     adapter_manager.start_auto_ml(req, uuid.uuid4())
    #     adapter_manager.start()
    #     adapter_manager.join()

    #     # check if model archive exists
    #     out_dir = os.path.join("app-data", "training",
    #                            req.user_id, req.dataset_id, req.training_id)
    #     path_to_model = os.path.join(out_dir, "export", "gluon-export.zip")
    #     self.assertTrue(os.path.exists(path_to_model), f"path to model: '{path_to_model}' exist")

    #     # clean up
    #     shutil.rmtree(out_dir)

    def test_text_regression(self):

        dataset_path = load_math_dataset()


        req = StartAutoMlRequest()
        req.training_id = "test"
        req.dataset_id = "test"
        req.user_id = "test"
        req.dataset_path = dataset_path
        req.configuration.task = ':tabular_regression'
        req.configuration.target = "signature"
        req.configuration.runtime_limit = 3
        req.configuration.metric = ':accuracy'
        req.configuration.parameters = {":metric": {"values": [":mean_squared_error"]}}
        req.dataset_configuration = json.dumps({
            "column_datatypes": {
                "chern_simons": ":float",
                "signature":":int",
                "cusp_volume":":float",
                "hyperbolic_adjoint_torsion_degree":":int",
                "hyperbolic_torsion_degree":":int",
                "injectivity_radius":":float",
                "longitudinal_translation":":float",
                "meridinal_translation_imag":":float",
                "meridinal_translation_real":":float",
                "short_geodesic_imag_part":":float",
                "short_geodesic_real_part":":float",
                "Symmetry_0":":float",
                "Symmetry_D3":":float",
                "Symmetry_D4":":float",
                "Symmetry_D6":":float",
                "Symmetry_D8":":float",
                "Symmetry_Z/2 + Z/2	":":float",
                "volume":":float"

            },
            "file_configuration": {
                "use_header": True,
                "start_row": 1,
                "delimiter": "comma",
                "escape_character": "\\",
                "decimal_character": ".",
                "thousands_seperator": ",",
                "datetime_format": "",
                "encoding": "utf-8"
            },
            "schema": {
                "signature": {
                    "datatype_detected": ":int",
                    "role_selected": ":target"
                }
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
