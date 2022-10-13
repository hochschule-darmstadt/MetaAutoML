from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property
from autogluon.tabular import TabularPredictor

class AutoGluonAdapterManager(AdapterManager):

    def __init__(self) -> None:
        super(AutoGluonAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "gluon"

    def _get_ml_model_and_lib(self, config):
        working_dir = config.result_folder_location
        # extract additional information from automl
        automl = TabularPredictor.load(os.path.join(os.path.join(working_dir, 'model_gluon.gluon')))
        automl_info = automl._learner.get_info(include_model_info=True)
        librarylist = set()
        #model = automl_info['best_model']
        model = ":ensemble"
        for model_info in automl_info['model_info']:
            if model_info == model:
                pass
            elif model_info in ('LightGBM', 'LightGBMXT'):
                librarylist.add(":lightgbm_lib")
            elif model_info == 'XGBoost':
                librarylist.add(":xgboost_lib")
            elif model_info == 'CatBoost':
                librarylist.add(":catboost_lib")
            elif model_info == 'NeuralNetFastAI':
                librarylist.add(":pytorch_lib")
            else:
                librarylist.add(":scikit_learn_lib")
        library = " + ".join(librarylist)
        #TODO correct read and array handling
        return librarylist.pop(), model

    def _load_model_and_make_probabilities(self, config_json, result_folder_location, dataframe):
        # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
        if self._loaded_training_id != config_json["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            self.__automl = TabularPredictor.load(os.path.join(result_folder_location, 'model_gluon.gluon'))
            self._loaded_training_id = config_json["training_id"]
        # Get prediction probabilities and send them back.
        probabilities = json.dumps(self.__automl.predict_proba(dataframe).values.tolist())
        return probabilities
