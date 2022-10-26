from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import json, logging, os, datetime
from AdapterRuntimeScheduler import AdapterRuntimeScheduler

class PredictionManager:
    
    def __init__(self, data_storage: DataStorage, adapter_runtime_scheduler: AdapterRuntimeScheduler) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__adapter_runtime_scheduler: AdapterRuntimeScheduler = adapter_runtime_scheduler
        self.__log = logging.getLogger('PredictionManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))


    def create_prediction(
        self, create_prediction_request: "CreatePredictionRequest"
    ) -> "CreatePredictionResponse":
        """Create a new prediction record and start prediction process

        Args:
            create_prediction_request (CreatePredictionRequest): GRPC message holding the user id, live dataset- and prediction informations

        Returns:
            CreatePredictionResponse: The empty GRPC response message
        """
        response = CreatePredictionResponse()


        self.__log.debug(f"create_training: generating training details")
        config = {
            "model_id": create_prediction_request.model_id,
            "live_dataset_path": "",
            "prediction_path": "",
            "status": "busy",
            "runtime_profile": {
                "start_time": datetime.datetime.now(),
                "end_time": datetime.datetime.now()
            },
            "lifecycle_state": "active"
        }
        
        self.__log.debug(f"create_prediction: saving new prediction {config} for user {create_prediction_request.user_id}")
        prediction_id: str = self.__data_storage.create_prediction(create_prediction_request.user_id, create_prediction_request.live_dataset_file_name, config)
        self.__log.debug(f"create_prediction: new prediction saved id: {prediction_id}")

        self.__adapter_runtime_scheduler.create_new_prediction(create_prediction_request.user_id, prediction_id)



        return response

    def __prediction_object_to_rpc_object(self, user_id: str, prediction: dict) -> Dataset:
        """Convert a prediction record dictionary into the GRPC Prediction object

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            prediction (dict): The retrieved prediction record dictionary

        Raises:
            grpclib.GRPCError: grpclib.Status.UNAVAILABLE, raised when a dictionary field could not be read

        Returns:
            Dataset: The GRPC prediction object generated from the dictonary
        """
        try:
            prediction_info = Prediction()
            prediction_info.id = str(prediction["_id"])
            prediction_info.model_id = prediction["model_id"]
            prediction_info.live_dataset_path = prediction["live_dataset_path"]
            prediction_info.prediction_path = prediction["prediction_path"]
            prediction_info.status = prediction["status"]

            prediction_runtime_profile = PredictionRuntimeProfile()
            prediction_runtime_profile.start_time = prediction["runtime_profile"]["start_time"]
            prediction_runtime_profile.end_time = prediction["runtime_profile"]["end_time"]
            prediction_info.runtime_profile = prediction_runtime_profile
            return prediction_info
        except Exception as e:
            self.__log.error(f"__prediction_object_to_rpc_object: Error while reading parameter for prediction {str(prediction['_id'])} for user {user_id}")
            self.__log.error(f"__prediction_object_to_rpc_object: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Prediciton {str(prediction['_id'])} for user {user_id}")
                

    def get_predictions(
        self, get_predictions_request: "GetPredictionsRequest"
    ) -> "GetPredictionsResponse":
        """Get all predictions by model

        Args:
            get_predictions_request (GetPredictionsRequest): The GRPC request holding the user id and model id

        Returns:
            GetPredictionsResponse: The GRPC response holding the list of found predictions
        """
        response = GetPredictionsResponse()
        self.__log.debug(f"get_predictions: get all prediction datasets for user {get_predictions_request.user_id}")
        all_predictions: list[dict[str, object]] = self.__data_storage.get_predictions(get_predictions_request.user_id, get_predictions_request.model_id)
        self.__log.debug(f"get_predictions: found {all_predictions.count} prediction datasets for user {get_predictions_request.user_id}")
        for prediction in all_predictions:
            response.predictions.append(self.__prediction_object_to_rpc_object(get_predictions_request.user_id, prediction))
        return response

    def get_prediction(
        self, get_prediction_request: "GetPredictionRequest"
    ) -> "GetPredictionResponse":
        """Get prediction details for a specific prediction

        Args:
            get_prediction_request (GetPredictionRequest): The GRPC request holding the user id and and prediction id

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if no dataset record was found

        Returns:
            GetPredictionResponse: The GRPC response holding the found prediction
        """
        response = GetPredictionResponse()
        self.__log.debug(f"get_prediction: trying to get prediction dataset {get_prediction_request.prediction_id} for user {get_prediction_request.user_id}")
        found, prediction = self.__data_storage.get_prediction(get_prediction_request.user_id, get_prediction_request.prediction_id)
        if not found:
            self.__log.error(f"get_prediction: prediction {get_prediction_request.prediction_id} for user {get_prediction_request.user_id} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {get_prediction_request.prediction_id} for user {get_prediction_request.user_id} not found, already deleted?")
        
        response.prediction = self.__prediction_object_to_rpc_object(get_prediction_request.user_id, prediction)
        return response

    def delete_prediction(
        self, delete_prediction_request: "DeletePredictionRequest"
    ) -> "DeletePredictionResponse":
        """Delete a prediction from database and disc

        Args:
            delete_prediction_request (DeletePredictionRequest): The GRPC request containing the user id, prediction id

        Returns:
            DeletePredictionResponse: The empty GRPC response
        """
        self.__log.debug(f"delete_prediction: deleting prediction dataset {delete_prediction_request.prediction_id}, of user {delete_prediction_request.user_id}")
        result = self.__data_storage.delete_prediction(delete_prediction_request.user_id, delete_prediction_request.prediction_id)
        self.__log.debug(f"delete_prediction: {str(result)} prediction datasets deleted")
        return DeletePredictionResponse()