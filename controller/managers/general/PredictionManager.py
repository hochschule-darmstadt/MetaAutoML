from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import json, logging, os

class PredictionManager:
    
    def __init__(self, data_storage: DataStorage) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('PredictionManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))

    def create_prediction(
        self, create_dataset_request: "CreatePredictionRequest"
    ) -> "CreatePredictionResponse":
        """
        Upload a new dataset
        ---
        Parameter
        1. dataset information
        ---
        Return empty CreateDatasetResponse object
        """
        self.__log.debug(f"create_prediction: saving new prediction dataset {create_dataset_request.prediction_name} for user {create_dataset_request.user_id}, with filename {create_dataset_request.file_name}, with dataset id {create_dataset_request.dataset_id}")
        dataset_id: str = self.__data_storage.create_prediction(create_dataset_request.user_id, create_dataset_request.file_name, create_dataset_request.dataset_id, create_dataset_request.file_name)
        self.__log.debug(f"create_prediction: new prediction dataset saved id: {dataset_id}")
        response = CreatePredictionResponse()
        return response

    def get_predictions(
        self, get_predictions_request: "GetPredictionsRequest"
    ) -> "GetPredictionsResponse":
        """
        Get all datasets for a specific task
        ---
        Parameter
        1. grpc request object, containing the user id
        ---
        Return a list of compatible datasets or a GRPC error UNAVAILABLE for read errors
        """
        response = GetPredictionsResponse()
        self.__log.debug(f"get_predictions: get all prediction datasets for user {get_predictions_request.user_id} and dataset id {get_predictions_request.dataset_id}")
        all_datasets: list[dict[str, object]] = self.__data_storage.get_predictions(get_predictions_request.user_id, get_predictions_request.dataset_id)
        
        self.__log.debug(f"get_predictions: found {all_datasets.count} prediction datasets for user {get_predictions_request.user_id}")
        for dataset in all_datasets:
            try:
                response_dataset = Prediction()
                
                response_dataset.id = str(dataset["_id"])
                response_dataset.name = dataset["name"]
                response_dataset.type = dataset['type']
                response_dataset.creation_time = datetime.fromtimestamp(int(dataset["creation_time"]))
                response_dataset.size = dataset['size']
                response_dataset.path = dataset["path"]
                response_dataset.file_name = dataset["file_name"]
                for model_item in dataset['predictions'].keys():
                    model_prediction = ModelPrediction()
                    for prediction_item in dataset['predictions'][model_item].keys():
                        prediction = Prediction()
                        prediction.creation_time = datetime.fromtimestamp(int(dataset['predictions'][model_item][prediction_item]['creation_time']))
                        prediction.status = dataset['predictions'][model_item][prediction_item]['status']
                        prediction.prediction_path = dataset['predictions'][model_item][prediction_item]['prediction_path']
                        prediction.prediction_time = dataset['predictions'][model_item][prediction_item]['prediction_time']
                        model_prediction.predictions[prediction_item] = prediction
                    response_dataset.predictions[model_item] = model_prediction
                response.predictions.append(response_dataset)
            except Exception as e:
                self.__log.error(f"get_predictions: Error while reading parameter prediction dataset for dataset {get_predictions_request.dataset_id} for user {get_predictions_request.user_id}")
                self.__log.error(f"get_predictions: exception: {e}")
                raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Prediciton Dataset for dataset {get_predictions_request.dataset_id} for user {get_predictions_request.user_id}")
                
        return response

    def get_prediction(
        self, get_prediction_request: "GetPredictionRequest"
    ) -> "GetPredictionResponse":
        """
        Get dataset details for a specific dataset
        ---
        Parameter
        1. grpc request object, containing the user, and dataset id
        ---
        Return dataset details
        The result is a GetDatasetResponse object describing one dataset or a GRPC error if ressource NOT_FOUND or UNAVAILABLE for read errors
        """
        response = GetPredictionResponse()
        self.__log.debug(f"get_prediction: trying to get prediction dataset {get_prediction_request.prediction_id} for user {get_prediction_request.user_id}")
        found, dataset = self.__data_storage.get_prediction(get_prediction_request.user_id, get_prediction_request.prediction_id)
        if not found:
            self.__log.error(f"get_prediction: dataset {get_prediction_request.prediction_id} for user {get_prediction_request.user_id} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {get_prediction_request.prediction_id} for user {get_prediction_request.user_id} not found, already deleted?")
        try:
            response_dataset = Prediction()
            response_dataset.id = str(dataset["_id"])
            response_dataset.name = dataset["name"]
            response_dataset.type = dataset['type']
            response_dataset.creation_time = datetime.fromtimestamp(int(dataset["creation_time"]))
            response_dataset.size = dataset['size']
            response_dataset.path = dataset["path"]
            response_dataset.file_name = dataset["file_name"]
            for model_item in dataset['predictions'].keys():
                model_prediction = ModelPrediction()
                for prediction_item in dataset['predictions'][model_item].keys():
                    prediction = Prediction()
                    prediction.creation_time = datetime.fromtimestamp(int(dataset['predictions'][model_item][prediction_item]['creation_time']))
                    prediction.status = dataset['predictions'][model_item][prediction_item]['status']
                    prediction.prediction_path = dataset['predictions'][model_item][prediction_item]['prediction_path']
                    prediction.prediction_time = dataset['predictions'][model_item][prediction_item]['prediction_time']
                    model_prediction.predictions[prediction_item] = prediction
                response_dataset.predictions[model_item] = model_prediction
            response.prediction = response_dataset
        except Exception as e:
            self.__log.error(f"get_prediction: Error while reading parameter for prediction dataset {get_prediction_request.prediction_id} for user {get_prediction_request.user_id}")
            self.__log.error(f"get_prediction: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Prediction Dataset {get_prediction_request.prediction_id} for user {get_prediction_request.user_id}")

                
        return response

    def delete_prediction(
        self, delete_prediction_request: "DeletePredictionRequest"
    ) -> "DeletePredictionResponse":
        """
        Delete a dataset from database and disc
        ---
        Parameter
        1. grpc request object containing the user id, dataset id
        ---
        Return empty DeleteDatasetResponse object or a GRPC error if ressource NOT_FOUND
        """
        self.__log.debug(f"delete_prediction: deleting prediction dataset {delete_prediction_request.prediction_id}, of user {delete_prediction_request.user_id}")
        result = self.__data_storage.delete_prediction(delete_prediction_request.user_id, delete_prediction_request.prediction_id)
        self.__log.debug(f"delete_prediction: {str(result)} prediction datasets deleted")
        return DeletePredictionResponse()