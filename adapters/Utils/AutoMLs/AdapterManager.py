import json
import os
import time, asyncio
import queue
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property
import pandas as pd
from typing import Tuple
import re

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
        self.__auto_ml_status_messages = queue.Queue()
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
        raise Exception("_get_ml_model_and_lib has to be implemented in sub class")

    async def __background_start_auto_ml(self):
        """Sets up the training run environment and start the background AutoML solution process. While the AutoML solution is running, collect all console messages and create the result messages.
        After the process concludes create the result archive and test the found model with the test set.
        """
        try:
            self.__start_auto_ml_running = True
            # saving AutoML configuration JSON
            config = setup_run_environment(self.__start_auto_ml_request, self._adapter_name)

            # start training process
            process = start_automl_process(config)

            # read the processes output line by line and push them onto the event queue
            for line in process.stdout:
                status_update = GetAutoMlStatusResponse()
                # if return Code is ADAPTER_RETURN_CODE_STATUS_UPDATE we do not have score values yet
                status_update.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_STATUS_UPDATE
                status_update.status_update = line

                # write line to this processes stdout
                sys.stdout.write(line)
                sys.stdout.flush()

                self.__auto_ml_status_messages.put(status_update)

            process.stdout.close()
            process.wait()

            generate_script(config)
            output_json = zip_script(config)
            #AutoKeras only produces keras based ANN
            library, model = self._get_ml_model_and_lib(config)
            # TODO: fix evaluation (does not work with image datasets)
            test_score, prediction_time = evaluate(config, os.path.join(config.job_folder_location, get_config_property("job-file-name")))
            self.__auto_ml_status_messages.put(get_response(output_json, test_score, prediction_time, library, model))

            print(f'{get_config_property("adapter-name")} job finished')
            self.__start_auto_ml_running = False

        except Exception as e:
            # always crash if we are not running in production environment
            if get_config_property("local_execution") == "YES":
                # reraise exception above to crash
                raise e
            else:
                # do not crash in prodution environment
                self.__start_auto_ml_running = False
                status_update = GetAutoMlStatusResponse()
                status_update.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_ERROR
                self.__auto_ml_status_messages.put(status_update)


    def get_auto_ml_status(self) -> "GetAutoMlStatusResponse":
        """Retrive the latest status message created by the AutoML solution subprocess if one is available. If no new message is available while the process is running, a message will be return with the status code set to PENDING

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if the AutoML solution subprocess is not running and there is no messages left in the message list

        Returns:
            GetAutoMlStatusResponse: return a GetAutoMlStatusResponse message holding the current AutoML solution training state
        """
        try:
            # try to fetch the first message in the queue
            return self.__auto_ml_status_messages.get_nowait()
        # will be raised when there is no message in the queue
        except queue.Empty:
            if self.__start_auto_ml_running:
                # no update, but training is ongoing
                response = GetAutoMlStatusResponse()
                response.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_PENDING
                return response
            else:
                # invalid request: no updates and training is not running
                raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Adapter session {self.__session_id} endded and no messages are left!")

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
            print("adapatermanager explain")
            config_json = json.loads(explain_auto_ml_request.process_json)
            config_json["dataset_configuration"] = json.loads(config_json["dataset_configuration"])
            result_folder_location = os.path.join(get_config_property("training-path"),
                                                  config_json["user_id"],
                                                  config_json["dataset_id"],
                                                  config_json["training_id"],
                                                  get_config_property("result-folder-name"))

            #For WSL users we need to adjust the path prefix for the dataset location to windows path
            if get_config_property("local_execution") == "YES":
                if get_config_property("running_in_wsl") == "YES":
                    config_json["dataset_path"] = re.sub("[a-zA-Z]:/([A-Za-z0-9]+(/[A-Za-z0-9]+)+)/MetaAutoML", get_config_property("wsl_metaautoml_path"), config_json["dataset_path"])
                    config_json["dataset_path"] = config_json["dataset_path"].replace("\\", "/")



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

            #load old dataset_configuration and save it to config json in case the dataset types have been changed in the
            #AutoKeras adapter for TextClassification
            #For WSL users we need to adjust the path prefix for the dataset location to windows path
            if get_config_property("local_execution") == "YES":
                if get_config_property("running_in_wsl") == "YES":
                    config_json["live_dataset_path"] = re.sub("[a-zA-Z]:/([A-Za-z0-9]+(/[A-Za-z0-9]+)+)/MetaAutoML", get_config_property("wsl_metaautoml_path"), config_json["live_dataset_path"])
                    config_json["live_dataset_path"] = config_json["live_dataset_path"].replace("\\", "/")

            with open(job_file_location) as file:
                config_json_old_dataset_configuation = json.load(file)

            config_json['dataset_configuration'] = config_json_old_dataset_configuation['dataset_configuration']

            # saving AutoML configuration JSON
            with open(job_file_location, "w+") as f:
                json.dump(config_json, f)

            prediction_time, result_path = predict(config_json, job_file_location, get_config_property("adapter-name"))
            response = PredictModelResponse()
            response.result_path = result_path
            return response

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while generating probabilities {e}")

    def get_start_auto_ml_request(self) -> StartAutoMlRequest:
        return self.__start_auto_ml_request

