import threading
from urllib import request
from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import json, logging, os

class ModelManager:

    def __init__(self, data_storage: DataStorage) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('ModelManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))


    def __model_object_to_rpc_object(self, user_id, model):
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
            model_info.test_score = model["test_score"]
            model_info.prediction_time =  model["prediction_time"]

            model_runtime_profile = ModelruntimeProfile()
            model_runtime_profile.start_time = model["runtime_profile"]["start_time"]
            model_runtime_profile.end_time = model["runtime_profile"]["end_time"]
            model_info.runtime_profile = model_runtime_profile

            model_info.status_messages[:] =  model["status_messages"]
            model_info.explanation = json.dumps(model["explanation"])
            return model_info
        except Exception as e:
            self.__log.error(f"__model_object_to_rpc_object: Error while reading parameter for model {model.model_id}")
            self.__log.error(f"__model_object_to_rpc_object: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model {model.model_id}")
            

    def get_models(
        self, get_models_request: "GetModelsRequest"
    ) -> "GetModelsResponse":
        """
        Get all models for a specific dataset
        ---
        Parameter
        1. grpc request object, containing the user and dataset id
        ---
        Return a list of compatible trainings or a GRPC error UNAVAILABLE for read errors
        """
        response = GetModelsResponse()
        def GetScore(e):
            return e["test_score"]

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
        """
        Get model details for a specific model
        ---
        Parameter
        1. grpc request object, containing the user, and traininig id
        ---
        Return model details
        The result is a GetTrainingResponse object describing one model or a GRPC error if ressource NOT_FOUND or UNAVAILABLE for read errors
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
        """
        Delete a model from database and disc
        ---
        Parameter
        1. grpc request object containing the user, model id
        ---
        Return empty DeleteModelResponse object or a GRPC error if ressource NOT_FOUND
        """
        self.__log.debug(f"delete_model: deleting model {delete_model_request.model_id}, of user {delete_model_request.user_id}")
        result = self.__data_storage.delete_model(delete_model_request.user_id, delete_model_request.model_id)
        self.__log.debug(f"delete_model: {str(result)} models deleted")
        return DeleteModelResponse()

