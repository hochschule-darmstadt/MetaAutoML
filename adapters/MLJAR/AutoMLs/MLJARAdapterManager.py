from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property
from supervised.automl import AutoML

class MLJARAdapterManager(AdapterManager):

    def __init__(self) -> None:
        super(MLJARAdapterManager, self).__init__()

    def _get_ml_model_and_lib(self, config):
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
        return library, model

    def _load_model_and_make_probabilities(self, config_json, result_folder_location, dataframe):
        # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
        if self._loaded_training_id != config_json["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            self._automl = AutoML(results_path=os.path.join(result_folder_location, "Models"))
            self._loaded_training_id = config_json["training_id"]
        # Get prediction probabilities and send them back.
        probabilities = json.dumps(self._automl.predict_proba(dataframe).tolist())
        return probabilities

   