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
from predict_time_sources import feature_preparation

class EvalMLAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self) -> None:
        """Initialize a new FLAMLAdapterManager setting AutoML adapter specific variables
        """
        super(EvalMLAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "evalml"

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
        #TODO ADD CORRECT lib and model display
        library = ":lightgbm_lib"
        model = ":light_gradient_boosting_machine"
        return library, model


    def _load_model_and_make_probabilities(self, config: "StartAutoMlRequest", result_folder_location: str, dataframe: pd.DataFrame):
        if self._loaded_training_id != config["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            with open(result_folder_location + '/evalml.p', 'rb') as file:
                self.__automl = dill.load(file)
            self._loaded_training_id = config["training_id"]
        try:
            probabilities = json.dumps(self.__automl.predict_proba(dataframe).values.tolist())
        except Exception as e:
            raise(e)
        return probabilities

    