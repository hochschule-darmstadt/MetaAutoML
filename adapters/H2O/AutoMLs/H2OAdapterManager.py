from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
# from H2OWrapper import H2OWrapper
from JsonUtil import get_config_property
import pandas as pd
from typing import Tuple
from explainerdashboard import ClassifierExplainer, RegressionExplainer, ExplainerDashboard
import h2o
import sys

class H2OAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self) -> None:
        """Initialize a new H2OAdapterManager setting AutoML adapter specific variables
        """
        super(H2OAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "h2o_automl"

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
        # start h2o
        h2o.init()

        # load model
        winnermodel = h2o.load_model(os.path.join(config.result_folder_location, 'model_h2o.p'))

        # get Type
        model_type = type(winnermodel).__name__

        lib = [
                    ":h2o_lib",
                    #":xgboost_lib" not implemented yet, but possible
                ]

        # Map Type
        if model_type == 'H2ODeepLearningEstimator':
            model_name = ":artificial_neural_network"
        elif model_type == 'H2ORandomForestEstimator':
            model_name = ":distributed_random_forest"
        elif model_type == 'H2OGradientBoostingEstimator':
            model_name = ":gradient_boosting_tree"
        elif model_type == 'H2OStackedEnsembleEstimator':
            model_name = ":stacking_ensemble"
        else:
            raise Exception("H2O AdapterManager: Unbekannter Modelltyp: " + model_type)

        # return name
        return (lib,model_name)

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
            h2o.init()
            self.__automl = h2o.load_model(os.path.join(result_folder_location, 'model_h2o.p'))

            self._loaded_training_id = config["training_id"]
            # Get prediction probabilities and send them back.
        probabilities = self.__automl.predict(np.array(dataframe.values.tolist()))

        return probabilities

