import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property
import pandas as pd
from typing import Tuple

class AdapterManager(Thread):
    """The base adapter manager object providing the shared functionality between all adapters

    Args:
        Thread (Thread): Allowing the AdapterManager to start a background thread
    """
    def __init__(self) -> None:
        """Initialize a new AdapterManager instance
        """
        super(AdapterManager, self).__init__()
        self.__session_id = ""
        self.__start_auto_ml_running = False
        self.__auto_ml_status_messages = []
        self.__start_auto_ml_request: StartAutoMlRequest = None
        self.__on_explain_finished_callback = ""
        self.__on_prediction_finished_callback = ""
        self._automl = None
        self._loaded_training_id = None

    def run(self):
        """Start the AutoML solution as a background process
        """
        asyncio.run(self.__background_start_auto_ml())
    
    def start_auto_ml(self, start_auto_ml_request: "StartAutoMlRequest", session_id: str):
        """Initiate the new AutoML search process

        Args:
            start_auto_ml_request (StartAutoMlRequest): The StartAutoMlRequest message holding the training configuration
            session_id (str): The unique session id, identifying the current session
        """
        self.__start_auto_ml_request = start_auto_ml_request
        self.__session_id = session_id

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Must be overwriten! Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
        return ("", "")

    async def __background_start_auto_ml(self):
        """Sets up the training run environment and start the background AutoML solution process. While the AutoML solution is running, collect all console messages and create the result messages. 
        After the process concludes create the result archive and test the found model with the test set.
        """
        try:
            self.__start_auto_ml_running = True
            # saving AutoML configuration JSON
            config = setup_run_environment(self.__start_auto_ml_request, self._adapter_name)
            process = start_automl_process(config)
            for response in capture_process_output(process, False):
                self.__auto_ml_status_messages.append(response)
            generate_script(config)
            output_json = zip_script(config)
            #AutoKeras only produces keras based ANN
            library, model = self._get_ml_model_and_lib(config)
            test_score, prediction_time = evaluate(config, os.path.join(config.job_folder_location, get_config_property("job-file-name")))
            self.__auto_ml_status_messages.append(get_response(output_json, test_score, prediction_time, library, model))
            print(f'{get_config_property("adapter-name")} job finished')
            self.__start_auto_ml_running = False

        except Exception as e:
            self.__start_auto_ml_running = False
            self.__auto_ml_status_messages.append(get_except_response(e))


    def get_auto_ml_status(self) -> "GetAutoMlStatusResponse":
        """Retrive the latest status message created by the AutoML solution subprocess if one is available. If no new message is available while the process is running, a message will be return with the status code set to PENDING

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if the AutoML solution subprocess is not running and there is no messages left in the message list

        Returns:
            GetAutoMlStatusResponse: return a GetAutoMlStatusResponse message holding the current AutoML solution training state
        """
        if (len(self.__auto_ml_status_messages) == 0) and self.__start_auto_ml_running == False:
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Adapter session {self.__session_id} endded and no messages are left!")
        if (len(self.__auto_ml_status_messages) == 0) and self.__start_auto_ml_running == True:
            response = GetAutoMlStatusResponse()
            response.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_PENDING
            return response
        len(self.__auto_ml_status_messages)
        return self.__auto_ml_status_messages.pop(0)

    def _load_model_and_make_probabilities(self, config: "StartAutoMlRequest", result_folder_location: str, dataframe: pd.DataFrame):
        """Must be overwriten! Load the found model, and execute a prediction using the provided data to calculate the probability metric used by the ExplanableAI module inside the controller

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths
            result_folder_location (str): The absolute path leading to the model result location
            dataframe (DataFrame): The dataframe holding the dataset to execute a new prediction on
        """
        return

    async def explain_model(self, explain_auto_ml_request: "ExplainModelRequest") -> ExplainModelResponse:
        """Function for explaining a model. This returns the prediction probabilities for the data passed within the
        request.data.
        This loads the model and stores it in the adapter object. This is done because SHAP, the explanation module
        accesses this function multiple times and reloading the model every time would add overhead.
        The data transferred is reformatted by SHAP (regarding datatypes and column names). However, the AutoMLs
        struggle with this reformatting so the dataset is loaded separately and the datatypes and column names of the
        transferred data are replaced.

        Args:
            explain_auto_ml_request (ExplainModelRequest): The ExplainModelRequest holding the prediction data

        Raises:
            grpclib.GRPCError: grpclib.Status.UNAVAILABLE, raised when any error is raised during the prediction process

        Returns:
            ExplainModelResponse: The ExplainModelResponse message holding the prediction probabilities
        """
        try:
            config_json = json.loads(explain_auto_ml_request.process_json)
            result_folder_location = os.path.join(get_config_property("training-path"),
                                                  config_json["user_id"],
                                                  config_json["dataset_id"],
                                                  config_json["training_id"],
                                                  get_config_property("result-folder-name"))
                                                  
            if self._loaded_training_id != config_json["training_id"]:
                df, test = data_loader(config_json)
                self._dataframeX, y = prepare_tabular_dataset(df, config_json)

            # Reassemble dataset with the datatypes and column names from the preprocessed data and the content of the
            # transmitted data.
            df = pd.DataFrame(data=json.loads(explain_auto_ml_request.data), columns=self._dataframeX.columns)
            df = df.astype(dtype=dict(zip(self._dataframeX.columns, self._dataframeX.dtypes.values)))

            probabilities = self._load_model_and_make_probabilities(config_json, result_folder_location, df)

            return ExplainModelResponse(probabilities=probabilities)

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while generating probabilities {e}")


    async def predict_model(self, predict_model_request: "PredictModelRequest") -> "PredictModelResponse":
        """Load a previously found model to execute a new prediction on it using a live dataset uploaded by the user

        Args:
            predict_model_request (PredictModelRequest): The PredictModelRequest holding the prediction informations

        Raises:
            grpclib.GRPCError: grpclib.Status.UNAVAILABLE, raised when any error is raised during the prediction process

        Returns:
            PredictModelResponse: The PredictModelResponse message holding the prediction.csv result path
        """
        try:
            config_json = json.loads(predict_model_request.process_json)
            job_file_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_id"],
                                        config_json["dataset_id"],
                                        config_json["training_id"],
                                        get_config_property("job-folder-name"),
                                        get_config_property("job-file-name"))

            # saving AutoML configuration JSON
            with open(job_file_location, "w+") as f:
                json.dump(config_json, f)

            prediction_time, result_path = predict(config_json, job_file_location, get_config_property("adapter-name"))
            response = PredictModelResponse()
            response.result_path = result_path
            return response

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while generating probabilities {e}")
