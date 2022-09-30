import threading
from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import json, logging, os

class ModelManager:

    def __init__(self, data_storage: DataStorage) -> None:
        self.__data_storage: DataStorage = data_storage
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

        self.__log.debug(f"get_models: get all models for dataset {get_models_request.dataset_identifer} for user {get_models_request.user_identifier}")
        all_models: list[dict[str, object]] = self.__data_storage.get_models(get_models_request.user_identifier, dataset_identifier=get_models_request.dataset_identifer)
        self.__log.debug(f"get_models: found {all_models.count} models for dataset {get_models_request.dataset_identifer} for user {get_models_request.user_identifier}")
        
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
                model_info.dataset_identifier = model["dataset_identifer"]
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
            model_info.dataset_identifier = model["dataset_identifer"]
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
        model = self.__data_storage.get_model(model_predict_request.user_identifier, model_predict_request.model_idenfier)
        training = self.__data_storage.get_training(model_predict_request.user_identifier, model["training_identifier"])

        config = {
            "task": training["task"],
            "configuration": training["configuration"],
            "dataset_configuration": training["dataset_configuration"],
            "runtime_constraints": training["runtime_constraints"],
            "test_configuration": training["test_configuration"],
            "metric": training["metric"],
            "file_configuration": training["file_configuration"]
        }
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

