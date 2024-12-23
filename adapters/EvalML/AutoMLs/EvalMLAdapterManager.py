from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
import pandas as pd
from typing import Tuple
from predict_time_sources import feature_preparation
import evalml

from ThreadLock import ThreadLock

#TODO evalml estimators
evalml_estimators = {
    'Time Series Baseline Regression Pipeline' : (":baseline", ":baseline")
}

class EvalMLAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self, lock: ThreadLock) -> None:
        """Initialize a new FLAMLAdapterManager setting AutoML adapter specific variables
        """
        super(EvalMLAdapterManager, self).__init__(lock)
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
        working_dir = config.result_folder_location
        #TODO ADD CORRECT lib and model display
        library = [":lightgbm_lib"]
        model = [":light_gradient_boosting_machine"]
        with open(os.path.join(os.path.join(working_dir, 'evalml.p')), 'rb') as file:
            loaded_model = dill.load(file)
        return library, model

    async def explain_model(self, explain_auto_ml_request: "ExplainModelRequest") -> ExplainModelResponse:
        """override explain model function for evalml to specify the woodword structure for test data set.

        Args:
            explain_auto_ml_request (ExplainModelRequest): _description_

        Raises:
            grpclib.GRPCError: _description_

        Returns:
            ExplainModelResponse: _description_
        """
        try:
            config_json = json.loads(explain_auto_ml_request.process_json)
            result_folder_location = os.path.join(os.getenv("TRAINING_PATH"),
                                                  config_json["user_id"],
                                                  config_json["dataset_id"],
                                                  config_json["training_id"],
                                                  os.getenv("RESULT_FOLDER_NAME"))

            if self._loaded_training_id != config_json["training_id"]:
                df, test = data_loader(config_json)
                self._dataframeX, y = prepare_tabular_dataset(df, config_json)

            df = pd.DataFrame(data=json.loads(explain_auto_ml_request.data), columns=self._dataframeX.columns)
            df = df.astype(dtype=dict(zip(self._dataframeX.columns, self._dataframeX.dtypes.values)))
            # apply ww strurture into test data
            self._dataframeX.ww.init(name="train")
            df.ww.init(logical_types=self._dataframeX.ww.logical_types,semantic_tags=self._dataframeX.ww.semantic_tags )
            probabilities = self._load_model_and_make_probabilities(config_json, result_folder_location,df)
            return ExplainModelResponse(probabilities=probabilities)

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while generating probabilities {e}")

    async def explain_model(self, explain_auto_ml_request: "ExplainModelRequest") -> ExplainModelResponse:
        """override explain model function for evalml to specify the woodword structure for test data set.

        Args:
            explain_auto_ml_request (ExplainModelRequest): _description_

        Raises:
            grpclib.GRPCError: _description_

        Returns:
            ExplainModelResponse: _description_
        """
        try:
            config_json = json.loads(explain_auto_ml_request.process_json)
            config_json["dataset_configuration"] = json.loads(config_json["dataset_configuration"])
            result_folder_location = os.path.join(os.getenv("TRAINING_PATH"),
                                                  config_json["user_id"],
                                                  config_json["dataset_id"],
                                                  config_json["training_id"],
                                                  os.getenv("RESULT_FOLDER_NAME"))

            if self._loaded_training_id != config_json["training_id"]:

                #For WSL users we need to adjust the path prefix for the dataset location to windows path
                if os.getenv("LOCAL_EXECUTION") == "YES":
                    if os.getenv("RUNNING_IN_WSL") == "YES":
                        config_json["dataset_path"] = re.sub("[a-zA-Z]:\\\\([A-Za-z0-9_]+(\\\\[A-Za-z0-9_]+)+)\\\\MetaAutoML", os.getenv("WSL_METAAUTOML_PATH"), config_json["dataset_path"])
                        config_json["dataset_path"] = config_json["dataset_path"].replace("\\", "/")

                df, test = data_loader(config_json)
                self._dataframeX, y = prepare_tabular_dataset(df, config_json)

            df = pd.DataFrame(data=json.loads(explain_auto_ml_request.data), columns=self._dataframeX.columns)
            df = df.astype(dtype=dict(zip(self._dataframeX.columns, self._dataframeX.dtypes.values)))
            # apply ww strurture into test data
            self._dataframeX.ww.init(name="train")
            df.ww.init(logical_types=self._dataframeX.ww.logical_types,semantic_tags=self._dataframeX.ww.semantic_tags )
            probabilities = self._load_model_and_make_probabilities(config_json, result_folder_location,df)
            return ExplainModelResponse(probabilities=probabilities)

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while generating probabilities {e}")


    def _load_model_and_make_probabilities(self, config: "StartAutoMlRequest", result_folder_location: str, dataframe: pd.DataFrame):
        """Must be overwriten! Load the found model, and execute a prediction using the provided data to calculate the probability metric used by the ExplanableAI module inside the controller
        Dummy implementation to avoid error in controller (becasue there is a bug with expoted model)

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths
            result_folder_location (str): The absolute path leading to the model result location
            dataframe (DataFrame): The dataframe holding the dataset to execute a new prediction on

        Rerturn:
            probalities as json
        """

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

