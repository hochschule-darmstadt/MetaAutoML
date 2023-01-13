from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property
import pandas as pd
from typing import Tuple

class AutoPytorchAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self) -> None:
        """Initialize a new AutokerasAdapterManager setting AutoML adapter specific variables
        """
        super(AutoKerasAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "autokeras"

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
        working_dir = config.result_folder_location
        # extract additional information from automl
        with open(os.path.join(working_dir, 'model_pytorch.p'), 'rb') as file:
            automl = dill.load(file)
            librarylist = set()
            for model in automl.models_.values():
                if type(model.config) == str:
                    if model.config == "catboost":
                        librarylist.add(":catboost_lib")
                    elif model.config == "lgb":
                        librarylist.add(":lightgbm_lib")
                    else:
                        librarylist.add(":scikit_learn_lib")
                else:
                    librarylist.add(":pytorch_lib")
            model = ":ensemble"
            library = " + ".join(librarylist)
        return librarylist.pop(), model

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
            with open(result_folder_location + '/model_pytorch.p', 'rb') as file:
                self.__automl = dill.load(file)
            self._loaded_training_id = config["training_id"]
        # Get prediction probabilities and send them back.
        probabilities = self.__automl.predict_proba(dataframe)
        probabilities = probabilities.tolist()
        probabilities = json.dumps(probabilities)
        return probabilities
