import threading
from urllib import request
from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import json, logging, os, uuid
from AdapterRuntimeScheduler import AdapterRuntimeScheduler

class ModelManager:

    def __init__(self, data_storage: DataStorage, adapter_runtime_scheduler: AdapterRuntimeScheduler) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__adapter_runtime_scheduler: AdapterRuntimeScheduler = adapter_runtime_scheduler
        self.__log = logging.getLogger('ModelManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))


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
        
        for model in list(all_models):
            try:
                model_info = Model()
                model_info.id = str(model["_id"])
                model_info.automl = model["automl_name"]
                model_info.status = model["status"]
                model_info.status_messages[:] =  model["status_messages"]
                model_info.test_score =  model["test_score"]
                model_info.runtime =  model["runtime"]
                model_info.prediction_time =  model["prediction_time"]
                model_info.ml_model_type =  model["ml_model_type"]
                model_info.ml_library =  model["ml_library"]
                model_info.training_id = model["training_id"]
                model_info.dataset_id = model["dataset_id"]
                model_info.explanation = json.dumps(model["explanation"])
                response.models.append(model_info)
            except Exception as e:
                self.__log.error(f"get_models: Error while reading parameter for model")
                self.__log.error(f"get_models: exception: {e}")
                raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model")
            
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
        
        try:        
            model_info = Model()
            model_info.id = str(model["_id"])
            model_info.automl = model["automl_name"]
            model_info.status = model["status"]
            model_info.status_messages[:] =  model["status_messages"]
            model_info.test_score =  model["test_score"]
            model_info.runtime =  model["runtime"]
            model_info.prediction_time =  model["prediction_time"]
            model_info.ml_model_type =  model["ml_model_type"]
            model_info.ml_library =  model["ml_library"]
            model_info.training_id = model["training_id"]
            model_info.dataset_id = model["dataset_id"]
            model_info.explanation = json.dumps(model["explanation"])
            response.model = model_info
        except Exception as e:
            self.__log.error(f"get_model: Error while reading parameter for model {get_model_request.model_id}")
            self.__log.error(f"get_model: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model {get_model_request.model_id}")
            
        return response

    def model_predict(
        self, model_predict_request: "ModelPredictRequest"
    ) -> "ModelPredictResponse":
        """
        Start a new AutoML process as Test
        ---
        Parameter
        1. Run configuration
        ---
        Return start process status
        """ 
        prediction_id = str(uuid.uuid4())
        with self.__data_storage.lock():
            found, prediction = self.__data_storage.get_prediction(model_predict_request.user_id, model_predict_request.prediction_id)

            online_prediction_session = { 
                    "creation_time": datetime.timestamp(datetime.now()),
                    "status": "busy",
                    "prediction_path": "",
                    "prediction_time": 0
                }

            if model_predict_request.model_id not in prediction["predictions"].keys():
                prediction["predictions"][model_predict_request.model_id] = {}
            
            prediction["predictions"][model_predict_request.model_id][prediction_id] = online_prediction_session
            self.__data_storage.update_prediction(model_predict_request.user_id, model_predict_request.prediction_id, {
                "predictions": prediction["predictions"]
            })

        self.__adapter_runtime_scheduler.create_new_prediction(model_predict_request, prediction_id)
        return ModelPredictResponse()

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
        return DeleteDatasetResponse(result)

