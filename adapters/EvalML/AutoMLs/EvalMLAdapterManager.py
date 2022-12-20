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
import evalml

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
    
    async def explain_model(self, explain_auto_ml_request: "ExplainModelRequest") -> ExplainModelResponse:
       
        try:
            print("override explain")
            config_json = json.loads(explain_auto_ml_request.process_json)
            result_folder_location = os.path.join(get_config_property("training-path"),
                                                  config_json["user_id"],
                                                  config_json["dataset_id"],
                                                  config_json["training_id"],
                                                  get_config_property("result-folder-name"))


            df, test = data_loader(config_json)
            dfX, y = prepare_tabular_dataset(df, config_json)
            classification_type = "binary" if y.nunique() == 2 else "multiclass"


            

            train_data, test_data, train_target, test_target = evalml.preprocessing.split_data(dfX, y, problem_type=classification_type,test_size=0.1)
            # todo correctly change data to data from request
            df = pd.DataFrame(data=json.loads(explain_auto_ml_request.data), columns=dfX.columns)
            df = df.astype(dtype=dict(zip(dfX.columns, dfX.dtypes.values)))
            dfX.ww.init(name="train")

            df.ww.init(logical_types=dfX.ww.logical_types,semantic_tags=dfX.ww.semantic_tags )
            print(dfX.ww)
            print("--------------------")
            print(df.ww)
            #probabilities = self._load_model_and_make_probabilities(config_json, result_folder_location, train_data.ww.iloc[0:len(df)])
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
        #dfLen = len(dataframe.index)
        #probabilities = json.dumps([[0.5, 0.5]]*dfLen)
        #return probabilities
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

    