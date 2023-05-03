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
from autogluon.multimodal import MultiModalPredictor
from autogluon.timeseries import TimeSeriesPredictor
from typing import Tuple

#TODO do all estimators https://github.com/autogluon/autogluon/tree/master/tabular/src/autogluon/tabular/models
autogluon_estimators ={
    'Naive' : (":baseline", ":baseline"),
    'SeasonalNaive' : (":baseline", ":baseline"),
    'ETS' : (":sktime_lib", ":exponential_smoothing"),
    'Theta' : (":sktime_lib", ":theta_method"),
    'ARIMA' : (":sktime_lib", ":autoregressive_integrated_moving_average"),
    'AutoETS' : (":sktime_lib", ":exponential_smoothing"),
    'AutoGluonTabular' : (":as", ":as"),
    'WeightedEnsemble' : (":ensemble", ":ensemble"),
    'StackerEnsemble' : (":ensemble", ":ensemble"),
    'BaggedEnsemble' : (":ensemble",":ensemble"),
    'GreedyWeightedEnsemble' : (":ensemble",":ensemble"),
    'DeepAR' : (":pytorch_lib",":artificial_neural_network"),
    'SimpleFeedForward' : (":pytorch_lib",":artificial_neural_network"),
    'TemporalFusionTransformer' : (":pytorch_lib",":transformer"),
    'GreedyWeightedEnsemble' : ("",""),
    'GreedyWeightedEnsemble' : ("",""),
    'GreedyWeightedEnsemble' : ("",""),
    'GreedyWeightedEnsemble' : ("",""),
    'GreedyWeightedEnsemble' : ("",""),
    'GreedyWeightedEnsemble' : ("",""),
    'GreedyWeightedEnsemble' : ("",""),
}

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
        if config.configuration['task'] in [":tabular_classification", ":tabular_regression"]:
            #We load the model to check it is intact
            automl = TabularPredictor.load(os.path.join(os.path.join(working_dir, 'model_gluon.gluon')))
            model = [":ensemble"]
            #TODO correct read and array handling
            return ([':lightgbm_lib'], model)
        elif config.configuration['task'] in [":text_classification", ":text_regression", ":named_entity_recognition"]:
            #We load the model to check it is intact
            automl = MultiModalPredictor.load(os.path.join(os.path.join(working_dir, 'model_gluon.gluon')))
            return ([":pytorch_lib"], [":transformer"])
        elif config.configuration['task'] in [":time_series_forecasting"]:
            #We load the model to check it is intact
            automl = TimeSeriesPredictor.load(os.path.join(os.path.join(working_dir, 'model_gluon.gluon')))
            m1 = automl.get_model_best()
            asd = automl.get_model_names()
            return ([":pytorch_lib"], [":transformer"])
        else:
            #We load the model to check it is intact
            automl = MultiModalPredictor.load(os.path.join(os.path.join(working_dir, 'model_gluon.gluon')))
            return ([":pytorch_lib"], [":artificial_neural_network"])


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
