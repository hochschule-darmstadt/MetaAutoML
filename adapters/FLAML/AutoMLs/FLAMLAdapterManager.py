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

class FLAMLAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self) -> None:
        """Initialize a new FLAMLAdapterManager setting AutoML adapter specific variables
        """
        super(FLAMLAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "flaml"

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
        working_dir = config.result_folder_location
        models = list()
        libraries = list()
        # extract additional information from automl
        with open(os.path.join(working_dir, "model_flaml.p"), 'rb') as file:
            automl = dill.load(file)
            if config.configuration["task"] == ":text_classification":
                models.append(":transformer")
                libraries.append(":torch")
            else:
                for model in automl.model.estimators:
                    if model[0] == "lgbm":
                        libraries.append(":lightgbm_lib")
                        models.append(":light_gradient_boosting_machine")
                    elif model[0] == "extra_tree":
                        libraries.append(":scikit_learn_lib")
                        models.append(":extra_tree")
                    elif model[0] == "rf":
                        libraries.append(":scikit_learn_lib")
                        models.append(":random_forest")
                    elif model[0] == "xgboost":
                        libraries.append(":xgboost_lib")
                        models.append(":xgboost")
                    elif model[0] == "xgb_limitdepth":
                        libraries.append(":xgboost_lib")
                        models.append(":xgboost")
                    elif model[0] == "lrl1":
                        libraries.append(":scikit_learn_lib")
                        models.append(":logistic_regression")
                    elif model[0] == "lrl2":
                        libraries.append(":scikit_learn_lib")
                        models.append(":logistic_regression")
                    elif model[0] == "tft":
                        libraries.append(":pytorch_lib")
                        models.append(":temporal_fusion_transformer")
                    elif model[0] == "prophet":
                        libraries.append(":prophet_lib")
                        models.append(":prophet")
                    elif model[0] == "arima":
                        libraries.append(":pyflux_lib")
                        models.append(":autoregressive_integrated_moving_average")
                    elif model[0] == "sarimax":
                        libraries.append(":pyflux_lib")
                        models.append(":seasonal_autoregressive_integrated_moving_average_exogenous")
        return libraries, models


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
            with open(result_folder_location + '/model_flaml.p', 'rb') as file:
                self.__automl = dill.load(file)
            self._loaded_training_id = config["training_id"]
        # Get prediction probabilities and send them back.
        probabilities = self.__automl.predict_proba(dataframe)
        probabilities = probabilities.tolist()
        probabilities = json.dumps(probabilities)
        return probabilities

