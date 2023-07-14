import json
import os
import asyncio
from typing import Tuple
import queue
import sys
from codecarbon.output import EmissionsData
from AdapterUtils import *
from AdapterImageUtils import *
from AdapterLongitudinalUtils import *
from AdapterTabularUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property
import pandas as pd
from typing import Tuple
import re
from codecarbon import OfflineEmissionsTracker
from subprocess import Popen
from predict_time_sources import feature_preparation

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
            carbon_tracker = OfflineEmissionsTracker(country_iso_code="DEU", tracking_mode="process", log_level="error")
            # saving AutoML configuration JSON
            config = setup_run_environment(self.__start_auto_ml_request, self._adapter_name)
            #Start carbon recording
            carbon_tracker.start()

            #set encoding for the stream
            #because it occurs errors with windows-1252 set it to latin-1
            if "encoding" in json.loads(self.__start_auto_ml_request.dataset_configuration)["file_configuration"]:
                encoding = json.loads(self.__start_auto_ml_request.dataset_configuration)["file_configuration"]["encoding"]
            else:
                encoding = "latin-1"
            if encoding == "windows-1252" or encoding == "cp1252":
                encoding = "latin-1"

            # start training process
            python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")
            process = Popen([python_env, "AutoML.py", config.job_folder_location],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    universal_newlines=True, encoding=encoding)

            # read the processes output line by line and push them onto the event queue
            for line in process.stdout:
                status_update = GetAutoMlStatusResponse()
                # if return Code is ADAPTER_RETURN_CODE_STATUS_UPDATE we do not have score values yet
                status_update.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_STATUS_UPDATE
                status_update.status_update = line
                status_update.emission_profile = CarbonEmission()
                # write line to this processes stdout
                sys.stdout.write(line)
                sys.stdout.flush()

                self.__auto_ml_status_messages.put(status_update)

            process.stdout.close()
            process.wait()
            #End carbon recording
            carbon_tracker.stop()
            #Read config configuration again as it might have been changed during the subprocess
            with open(os.path.join(config.job_folder_location, get_config_property("job-file-name"))) as file:
                updated_process_configuration = json.load(file)
            config.dataset_configuration = updated_process_configuration["dataset_configuration"]
            #incase of timeseries forcasting we need to extract the forecast horizon
            if config.configuration["task"] == ":time_series_forecasting":
                config.forecasting_horizon = updated_process_configuration["forecasting_horizon"]

            generate_script(config)
            output_json = zip_script(config)
            #AutoKeras only produces keras based ANN
            library, model = self._get_ml_model_and_lib(config)
            # TODO: fix evaluation (does not work with image datasets)
            test_score, prediction_time = evaluate(config, os.path.join(config.job_folder_location, get_config_property("job-file-name")))
            self.__auto_ml_status_messages.put(self.get_response(output_json, json.dumps(test_score), prediction_time, library, model, carbon_tracker.final_emissions_data))

            print(f'{get_config_property("adapter-name")} job finished')
            self.__start_auto_ml_running = False

        except Exception as e:
            # always crash if we are not running in production environment
            if get_config_property("local_execution") == "YES":
                # reraise exception above to crash
                raise e
            else:
                # do not crash in production environment
                self.__start_auto_ml_running = False
                status_update = GetAutoMlStatusResponse()
                status_update.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_ERROR
                self.__auto_ml_status_messages.put(status_update)
                if hasattr(e, "message"):
                    print(e.message)
                else:
                    print(e)

    def get_response(self, config: "StartAutoMlRequest", test_score: float, prediction_time: float, library: str, model: str, emissions: EmissionsData) -> "GetAutoMlStatusResponse":
        """Generate the final GRPC AutoML status message

        Args:
            config (StartAutoMlRequest): The StartAutoMlRequest request, extended with the trainings folder paths
            test_score (float): The test score archieve by the model
            prediction_time (float): The passed time to make one prediction using the model
            library (str): The ML library the model is based upon
            model (str): The ML model type the model is composed off

        Returns:
            GetAutoMlStatusResponse: The GRPS AutoML status messages
        """
        response = GetAutoMlStatusResponse()
        response.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_SUCCESS
        if get_config_property("local_execution") == "NO":
            response.path = os.path.join(config.controller_export_folder_location, config.file_name)
        else:
            response.path = os.path.abspath(os.path.join(config.file_location, config.file_name))
        response.test_score = test_score
        response.prediction_time = prediction_time
        response.ml_library = library
        response.ml_model_type = model

        #Add emission profile
        emission_profile = CarbonEmission()
        emission_profile.emissions = emissions.emissions
        emission_profile.emissions_rate = emissions.emissions_rate
        emission_profile.energy_consumed = emissions.energy_consumed
        emission_profile.duration = emissions.duration
        emission_profile.cpu_count = emissions.cpu_count
        emission_profile.cpu_energy = emissions.cpu_energy
        emission_profile.cpu_model = emissions.cpu_model
        emission_profile.cpu_power = emissions.cpu_power
        emission_profile.gpu_count = emissions.gpu_count
        emission_profile.gpu_energy = emissions.gpu_energy
        emission_profile.gpu_model = emissions.gpu_model
        emission_profile.gpu_power = emissions.gpu_power
        emission_profile.ram_energy = emissions.ram_energy
        emission_profile.ram_power = emissions.ram_power
        emission_profile.ram_total_size = emissions.ram_total_size

        response.emission_profile = emission_profile
        return response

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
            job_file_location = os.path.join(get_config_property("training-path"),
                                                  config_json["user_id"],
                                                  config_json["dataset_id"],
                                                  config_json["training_id"],
                                                  get_config_property("job-folder-name"),
                                                  get_config_property("job-file-name"))
            #Read dataset configuration
            with open(job_file_location) as file:
                updated_process_configuration = json.load(file)
            config_json["dataset_configuration"] = json.loads(updated_process_configuration["dataset_configuration"])

            # Reassemble dataset with the datatypes and column names from the preprocessed data and the content of the
            # transmitted data.
            features = []
            for column, dt in config_json["dataset_configuration"]["schema"].items():
                if dt.get("role_selected", "") != ":target":
                    features.append(column)
            X = pd.DataFrame(data=json.loads(explain_auto_ml_request.data), columns=features)
            X, y = prepare_tabular_dataset(X, config_json,  is_prediction=True)


            probabilities = self._load_model_and_make_probabilities(config_json, result_folder_location, X)

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

    def create_explainer_dashboard(self, request: "CreateExplainerDashboardRequest") -> "CreateExplainerDashboardResponse":
        """Must be overwriten! Creates the Explainerdashboard used by the ExplainableAIManager module inside the controller

        Args:
            config (CreateExplainerDashboardRequest): the request holding configuration data.
        """
        print(f"starting creating dashboard")

        dashboard_response = CreateExplainerDashboardResponse()

        try:
            from explainerdashboard import ClassifierExplainer, ExplainerDashboard, RegressionExplainer
            import sys, importlib
            importlib.reload(sys.modules['explainerdashboard'])
            from explainerdashboard import ClassifierExplainer, ExplainerDashboard, RegressionExplainer
            # The library is available
            print("explainerdashboard is installed.")
        except ImportError:
            # The library is not available
            print("explainerdashboard is not installed.")
            dashboard_response.compatible = False
            dashboard_response.path = ""
            return dashboard_response

        #try:
        config = json.loads(request.process_json)
        result_folder_location = os.path.join("app-data", "training",
                            config["user_id"], config["dataset_id"], config["training_id"], "result")
        #Read config configuration again as it might have been changed during the training
        job_folder_location = os.path.join(get_config_property("training-path"),
                                            config["user_id"],
                                            config["dataset_id"],
                                            config["training_id"],
                                            get_config_property("job-folder-name"),
                                            get_config_property("job-file-name"))
        dashboard_folder_location = os.path.join(get_config_property("training-path"),
                                            config["user_id"],
                                            config["dataset_id"],
                                            config["training_id"],
                                            get_config_property("dashboard-folder-name"))
        with open(job_folder_location) as file:
            updated_process_configuration = json.load(file)

        config["dataset_configuration"] = json.loads(updated_process_configuration["dataset_configuration"])

        with open(dashboard_folder_location + '/dashboard_model.p', 'rb') as file:
            pipeline_model = dill.load(file)

        train, test = data_loader(config)
        for column, dt in config["dataset_configuration"]["schema"].items():
            if dt.get("role_selected", "") == ":target":
                target = column
        #X, y = prepare_tabular_dataset(test, config)
        try:

            if config["configuration"]["task"] == ":tabular_classification" or config["configuration"]["task"] == ":text_classification" :
                explainer = ClassifierExplainer(pipeline_model, test.drop(target, axis=1), test[target])
                dashboard = ExplainerDashboard(explainer)
                dashboard.save_html(os.path.join(dashboard_folder_location, "binary_dashboard.html"))
                dashboard.explainer.dump(os.path.join(dashboard_folder_location, "binary_dashboard.dill"))

            else :
                dashboard = ExplainerDashboard(RegressionExplainer(pipeline_model, test.drop(target, axis=1), test[target]))
                dashboard.save_html(os.path.join(dashboard_folder_location, "binary_dashboard.html"))
                dashboard.explainer.dump(os.path.join(dashboard_folder_location, "binary_dashboard.dill"))
        except Exception as e:
            print(f"error: {e}")
        print(f"created dashboard")
        dashboard_response.path = os.path.join(dashboard_folder_location, "binary_dashboard.dill")
        dashboard_response.compatible = True

        return dashboard_response

    def get_start_auto_ml_request(self) -> StartAutoMlRequest:
        return self.__start_auto_ml_request

