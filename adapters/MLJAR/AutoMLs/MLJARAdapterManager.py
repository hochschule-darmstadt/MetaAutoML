from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from supervised.automl import AutoML
import pandas as pd
from typing import Tuple

from ThreadLock import ThreadLock

class MLJARAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self, lock: ThreadLock) -> None:
        """Initialize a new MLJARAdapterManager setting AutoML adapter specific variables
        """
        super(MLJARAdapterManager, self).__init__(lock)
        self._adapter_name = "mljar"

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
        working_dir = config.result_folder_location
        leaderboard = pd.read_csv(os.path.join(working_dir, "Models", "leaderboard.csv"))
        #print(leaderboard[leaderboard["metric_value"].eq(leaderboard["metric_value"].min())])
        #TODO add all constellations
        if leaderboard[leaderboard["metric_value"].eq(leaderboard["metric_value"].min())]["model_type"].values[0] == "Decision Tree":
            model = ":decision_tree"
            library = ":scikit_learn_lib"
        elif leaderboard[leaderboard["metric_value"].eq(leaderboard["metric_value"].min())]["model_type"].values[0] == "Ensemble":
            model = ":ensemble"
            library = ":scikit_learn_lib"
        else:
            model = ":ensemble"
            library = ":scikit_learn_lib"
        return [library], [model]

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
            self._automl = AutoML(results_path=os.path.join(result_folder_location, "Models"))
            self._loaded_training_id = config["training_id"]
        # Get prediction probabilities and send them back.
        probabilities = json.dumps(self._automl.predict_proba(dataframe).tolist())
        return probabilities

