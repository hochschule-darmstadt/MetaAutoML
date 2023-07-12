import threading
from urllib import request
from DataStorage import DataStorage
from ControllerBGRPC import *
import json, logging, os
from AdapterRuntimeScheduler import AdapterRuntimeScheduler

class ModelManager:
    """The ModelManager provides all functionality related to Models objects
    """

    def __init__(self, data_storage: DataStorage, adapter_runtime_scheduler: AdapterRuntimeScheduler) -> None:
        """Initialize a new ModelManager instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
        """
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('ModelManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__adapter_runtime_scheduler = adapter_runtime_scheduler


    def __model_object_to_rpc_object(self, user_id: str, model: dict) -> Model:
        """Convert a model record dictionary into the GRPC Model object

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model (dict): The retrieved model record dictionary

        Raises:
            grpclib.GRPCError: grpclib.Status.UNAVAILABLE, raised when a dictionary field could not be read

        Returns:
            Model: The GRPC model object generated from the dictonary
        """
        try:
            self.__log.debug("__model_object_to_rpc_object: get all predictions for model")
            model_predictions = self.__data_storage.get_predictions(user_id, str(model["_id"]))
            self.__log.debug(f"__model_object_to_rpc_object: found {model_predictions.count} predictions")

            model_info = Model()
            model_info.id = str(model["_id"])
            model_info.training_id = model["training_id"]

            for prediction in model_predictions:
                prediction_detail = Prediction()
                prediction_detail.id = str(prediction["_id"])
                prediction_detail.model_id = prediction["model_id"]
                prediction_detail.live_dataset_path = prediction["live_dataset_path"]
                prediction_detail.prediction_path = prediction["prediction_path"]
                prediction_detail.status = prediction["status"]
                prediction_runtime_profile = PredictionRuntimeProfile()
                prediction_runtime_profile.start_time = prediction["runtime_profile"]["start_time"]
                prediction_runtime_profile.end_time = prediction["runtime_profile"]["end_time"]
                prediction_detail.runtime_profile = prediction_runtime_profile
                model_info.predictions.append(prediction_detail)

            model_info.status = model["status"]
            model_info.auto_ml_solution = model["auto_ml_solution"]
            model_info.ml_model_type = model["ml_model_type"]
            model_info.ml_library =  model["ml_library"]
            model_info.path = model["path"]
            model_info.test_score = json.dumps(model["test_score"])
            model_info.prediction_time =  model["prediction_time"]

            model_runtime_profile = ModelruntimeProfile()
            model_runtime_profile.start_time = model["runtime_profile"]["start_time"]
            model_runtime_profile.end_time = model["runtime_profile"]["end_time"]
            model_info.runtime_profile = model_runtime_profile

            model_info.status_messages[:] =  model["status_messages"]
            #model_info.explanation = json.dumps(model["explanation"])
            model_info.dashboard_compatible = model.get("dashboard_compatible", False)

            if not "carbon_footprint" in model:
                        model["carbon_footprint"] = {"emissions": 0}
            model_info.emission = model["carbon_footprint"].get("emissions", 0)
            return model_info
        except Exception as e:
            self.__log.error(f"__model_object_to_rpc_object: Error while reading parameter for model {model.model_id}")
            self.__log.error(f"__model_object_to_rpc_object: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model {model.model_id}")


    def get_models(
        self, get_models_request: "GetModelsRequest"
    ) -> "GetModelsResponse":
        """Get all datasets or get all datasets using an optional filter

        Args:
            get_models_request (GetModelsRequest): The GRPC request holding the user id and filters

        Returns:
            GetModelsResponse: The GRPC response holding the list of found models
        """
        response = GetModelsResponse()
        def GetScore(e):
            score_list = list(e["test_score"].values())
            if len(score_list) == 0:
                return 0
            #we will always use the first score for comparision
            return score_list[0]

        self.__log.debug(f"get_models: get all models for dataset {get_models_request.dataset_id} for user {get_models_request.user_id}")
        all_models: list[dict[str, object]] = self.__data_storage.get_models(get_models_request.user_id, dataset_id=get_models_request.dataset_id)
        self.__log.debug(f"get_models: found {all_models.count} models for dataset {get_models_request.dataset_id} for user {get_models_request.user_id}")

        all_models.sort(key=GetScore, reverse=True)

        for model in all_models:
            response.models.append(self.__model_object_to_rpc_object(get_models_request.user_id, model))

        return response

    def get_model(
        self, get_model_request: "GetModelRequest"
    ) -> "GetModelResponse":
        """Get model details for a specific model

        Args:
            get_model_request (GetModelRequest): The GRPC request holding the user id and and model id

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if no model record was found

        Returns:
            GetModelResponse: The GRPC response holding the found model
        """
        response = GetModelResponse()
        found, model = self.__data_storage.get_model(get_model_request.user_id, get_model_request.model_id)
        if not found:
            self.__log.error(f"get_training: model {get_model_request.model_id} for user {get_model_request.user_id} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {get_model_request.model_id} for user {get_model_request.user_id} not found, already deleted?")

        response.model = self.__model_object_to_rpc_object(get_model_request.user_id, model)
        return response


    def delete_model(
        self, delete_model_request: "DeleteModelRequest"
    ) -> "DeleteModelResponse":
        """Delete a model from database and disc

        Args:
            delete_model_request (DeleteModelRequest): The GRPC request containing the user id, model id

        Returns:
            DeleteModelResponse: The empty GRPC response
        """
        self.__log.debug(f"delete_model: deleting model {delete_model_request.model_id}, of user {delete_model_request.user_id}")
        amount_delelted_models = self.__data_storage.delete_model(delete_model_request.user_id, delete_model_request.model_id)
        self.__log.debug(f"delete_model: model deleted {amount_delelted_models}")
        return DeleteModelResponse()

    def start_explainer_dashboard(
        self, start_dashboard_request: "StartDashboardRequest"
    ) -> "StartDashboardResponse":
        """Start an ExplainerDashboard from disc

        Args:
            start_dashboard_request (StartDashboardRequest): The GRPC request containing the model id

        Returns:
            start_dashboard_response: The empty GRPC response
        """
        self.__log.debug(f"start_explainer_dashboard: start dashboard of model {start_dashboard_request.model_id}")
        return self.__adapter_runtime_scheduler.start_new_explainer_dashboard(start_dashboard_request.user_id, start_dashboard_request.model_id)

    def stop_explainer_dashboard(
        self, stop_dashboard_request: "StopDashboardRequest"
    ) -> "StopDashboardResponse":
        """Stop an ExplainerDashboard

        Args:
            stop_dashboard_request (StioDashboardRequest): The GRPC request containing the model id

        Returns:
            stop_dashboard_response: The empty GRPC response
        """
        self.__log.debug(f"stop_explainer_dashboard: stop dashboard of session {stop_dashboard_request.session_id}")

        return self.__adapter_runtime_scheduler.stop_explainer_dashboard(stop_dashboard_request.session_id)
