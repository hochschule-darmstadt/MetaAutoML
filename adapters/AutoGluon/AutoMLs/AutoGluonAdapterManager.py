from AdapterManager import AdapterManager
import json
import os
import pandas as pd
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property
from autogluon.tabular import TabularPredictor
from typing import Tuple

class AutoGluonAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """


    def __init__(self) -> None:
        """Initialize a new AutoGluonAdapterManager setting AutoML adapter specific variables
        """
        super(AutoGluonAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "gluon"

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
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
        return (librarylist.pop(), model)

    def _load_model_and_make_probabilities(self, config: "StartAutoMlRequest", result_folder_location: str, dataframe: pd.DataFrame):
        """Must be overwriten! Load the found model, and execute a prediction using the provided data to calculate the probability metric used by the ExplanableAI module inside the controller

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths
            result_folder_location (str): The absolute path leading to the model result location
            dataframe (DataFrame): The dataframe holding the dataset to execute a new prediction on
        """
        # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
        if self._loaded_training_id != config["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            self.__automl = TabularPredictor.load(os.path.join(result_folder_location, 'model_gluon.gluon'))
            self._loaded_training_id = config["training_id"]
        # Get prediction probabilities and send them back.
        probabilities = json.dumps(self.__automl.predict_proba(dataframe).values.tolist())
        return probabilities
