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
        1. grpc request object, containing the user and dataset identifier
        ---
        Return a list of compatible trainings or a GRPC error UNAVAILABLE for read errors
        """
        response = GetModelsResponse()
        def GetScore(e):
            return e["test_score"]

        self.__log.debug(f"get_models: get all models for dataset {get_models_request.dataset_identifier} for user {get_models_request.user_identifier}")
        all_models: list[dict[str, object]] = self.__data_storage.get_models(get_models_request.user_identifier, dataset_identifier=get_models_request.dataset_identifier)
        self.__log.debug(f"get_models: found {all_models.count} models for dataset {get_models_request.dataset_identifier} for user {get_models_request.user_identifier}")
        
        all_models.sort(key=GetScore, reverse=True)
        
        for model in list(all_models):
            try:
                model_info = Model()
                model_info.identifier = str(model["_id"])
                model_info.automl = model["automl_name"]
                model_info.status = model["status"]
                model_info.status_messages[:] =  model["status_messages"]
                model_info.test_score =  model["test_score"]
                model_info.runtime =  model["runtime"]
                model_info.prediction_time =  model["prediction_time"]
                model_info.ml_model_type =  model["ml_model_type"]
                model_info.ml_library =  model["ml_library"]
                model_info.training_identifier = model["training_identifier"]
                model_info.dataset_identifier = model["dataset_identifier"]
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
        1. grpc request object, containing the user, and traininig identifier
        ---
        Return model details
        The result is a GetTrainingResponse object describing one model or a GRPC error if ressource NOT_FOUND or UNAVAILABLE for read errors
        """
        response = GetModelResponse()
        found, model = self.__data_storage.get_model(get_model_request.user_identifier, get_model_request.model_identifier)
        if not found:
            self.__log.error(f"get_training: model {get_model_request.model_identifier} for user {get_model_request.user_identifier} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {get_model_request.model_identifier} for user {get_model_request.user_identifier} not found, already deleted?")
        
        try:        
            model_info = Model()
            model_info.identifier = str(model["_id"])
            model_info.automl = model["automl_name"]
            model_info.status = model["status"]
            model_info.status_messages[:] =  model["status_messages"]
            model_info.test_score =  model["test_score"]
            model_info.runtime =  model["runtime"]
            model_info.prediction_time =  model["prediction_time"]
            model_info.ml_model_type =  model["ml_model_type"]
            model_info.ml_library =  model["ml_library"]
            model_info.training_identifier = model["training_identifier"]
            model_info.dataset_identifier = model["dataset_identifier"]
            model_info.explanation = json.dumps(model["explanation"])
            response.model = model_info
        except Exception as e:
            self.__log.error(f"get_model: Error while reading parameter for model {get_model_request.model_identifier}")
            self.__log.error(f"get_model: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model {get_model_request.model_identifier}")
            
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
        prediction_identifier = str(uuid.uuid4())
        with self.__data_storage.lock():
            found, prediction_dataset = self.__data_storage.get_prediction_dataset(model_predict_request.user_identifier, model_predict_request.prediction_dataset_identifier)

            online_prediction_session = { 
                    "prediction_identifier": prediction_identifier,
                    "model_identifier": model_predict_request.model_identifier,
                    "request_datetime": datetime.timestamp(datetime.now()),
                    "status": "created",
                    "result_path": ""
                }
            prediction_dataset["predictions"][prediction_identifier] = online_prediction_session
            self.__data_storage.update_prediction_dataset(model_predict_request.user_identifier, model_predict_request.prediction_dataset_identifier, {
                "predictions": prediction_dataset["predictions"]
            })

        self.__adapter_runtime_scheduler.create_new_prediction(model_predict_request, prediction_identifier)
        #TODO REWORK ONLINE PREDICTION
        #automl = AdapterManager(self.__data_storage)
        #test_auto_ml = automl.TestAutoml(model_predict_request, model["automl_name"], model["training_identifier"], config)
        #if test_auto_ml:
        #    response = TestAutoMlResponse()
        #    for prediction in test_auto_ml.predictions:
        #        response.predictions.append(prediction)
        #    response.score = test_auto_ml.score
        #    response.predictiontime = test_auto_ml.predictiontime
        #else:
        #    response = ModelPredictResponse()
        return ModelPredictResponse()

    def delete_model(
        self, delete_model_request: "DeleteModelRequest"
    ) -> "DeleteModelResponse":
        """
        Delete a model from database and disc
        ---
        Parameter
        1. grpc request object containing the user, model identifier
        ---
        Return empty DeleteModelResponse object or a GRPC error if ressource NOT_FOUND
        """
        self.__log.debug(f"delete_model: deleting model {delete_model_request.model_identifier}, of user {delete_model_request.user_identifier}")
        result = self.__data_storage.delete_model(delete_model_request.user_identifier, delete_model_request.model_identifier)
        self.__log.debug(f"delete_model: {str(result)} models deleted")
        return DeleteDatasetResponse(result)

