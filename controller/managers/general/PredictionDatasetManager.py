from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import json, logging, os

class PredictionDatasetManager:
    
    def __init__(self, data_storage: DataStorage) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('PredictionDatasetManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))

    def create_prediction_dataset(
        self, create_dataset_request: "CreatePredictionDatasetRequest"
    ) -> "CreatePredictionDatasetResponse":
        """
        Upload a new dataset
        ---
        Parameter
        1. dataset information
        ---
        Return empty CreateDatasetResponse object
        """
        self.__log.debug(f"create_prediction_dataset: saving new prediction dataset {create_dataset_request.prediction_dataset_name} for user {create_dataset_request.user_identifier}, with filename {create_dataset_request.file_name}, with dataset identifier {create_dataset_request.dataset_identifier}")
        dataset_id: str = self.__data_storage.create_prediction_dataset(create_dataset_request.user_identifier, create_dataset_request.file_name, create_dataset_request.dataset_identifier, create_dataset_request.file_name)
        self.__log.debug(f"create_prediction_dataset: new prediction dataset saved identifier: {dataset_id}")
        response = CreatePredictionDatasetResponse()
        return response

    def get_prediction_datasets(
        self, get_prediction_datasets_request: "GetPredictionDatasetsRequest"
    ) -> "GetPredictionDatasetsResponse":
        """
        Get all datasets for a specific task
        ---
        Parameter
        1. grpc request object, containing the user identifier
        ---
        Return a list of compatible datasets or a GRPC error UNAVAILABLE for read errors
        """
        response = GetPredictionDatasetsResponse()
        self.__log.debug(f"get_prediction_datasets: get all prediction datasets for user {get_prediction_datasets_request.user_identifier} and dataset identifier {get_prediction_datasets_request.dataset_identifier}")
        all_datasets: list[dict[str, object]] = self.__data_storage.get_prediction_datasets(get_prediction_datasets_request.user_identifier, get_prediction_datasets_request.dataset_identifier)
        
        self.__log.debug(f"get_prediction_datasets: found {all_datasets.count} prediction datasets for user {get_prediction_datasets_request.user_identifier}")
        for dataset in all_datasets:
            try:
                response_dataset = PredictionDataset()
                
                response_dataset.identifier = str(dataset["_id"])
                response_dataset.name = dataset["name"]
                response_dataset.type = dataset['type']
                response_dataset.creation_date = datetime.fromtimestamp(int(dataset["creation_time"]))
                response_dataset.size = dataset['size']
                response_dataset.analysis = json.dumps(dataset['analysis'])
                response_dataset.path = dataset["path"]
                response_dataset.file_name = dataset["file_name"]
                response_dataset.predictions = json.dumps(dataset['predictions'])
                response.prediction_datasets.append(response_dataset)
            except Exception as e:
                self.__log.error(f"get_prediction_datasets: Error while reading parameter prediction dataset for dataset {get_prediction_datasets_request.dataset_identifier} for user {get_prediction_datasets_request.user_identifier}")
                self.__log.error(f"get_prediction_datasets: exception: {e}")
                raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Prediciton Dataset for dataset {get_prediction_datasets_request.dataset_identifier} for user {get_prediction_datasets_request.user_identifier}")
                
        return response

    def get_prediction_dataset(
        self, get_prediction_dataset_request: "GetPredictionDatasetRequest"
    ) -> "GetPredictionDatasetResponse":
        """
        Get dataset details for a specific dataset
        ---
        Parameter
        1. grpc request object, containing the user, and dataset identifier
        ---
        Return dataset details
        The result is a GetDatasetResponse object describing one dataset or a GRPC error if ressource NOT_FOUND or UNAVAILABLE for read errors
        """
        response = GetPredictionDatasetResponse()
        self.__log.debug(f"get_prediction_dataset: trying to get prediction dataset {get_prediction_dataset_request.prediction_dataset_identifier} for user {get_prediction_dataset_request.user_identifier}")
        found, dataset = self.__data_storage.get_prediction_dataset(get_prediction_dataset_request.user_identifier, get_prediction_dataset_request.prediction_dataset_identifier)
        if not found:
            self.__log.error(f"get_prediction_dataset: dataset {get_prediction_dataset_request.prediction_dataset_identifier} for user {get_prediction_dataset_request.user_identifier} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {get_prediction_dataset_request.prediction_dataset_identifier} for user {get_prediction_dataset_request.user_identifier} not found, already deleted?")
        try:
            response_dataset = PredictionDataset()
            response_dataset.identifier = str(dataset["_id"])
            response_dataset.name = dataset["name"]
            response_dataset.type = dataset['type']
            response_dataset.creation_date = datetime.fromtimestamp(int(dataset["creation_time"]))
            response_dataset.size = dataset['size']
            response_dataset.analysis = json.dumps(dataset['analysis'])
            response_dataset.path = dataset["path"]
            response_dataset.file_name = dataset["file_name"]
            response_dataset.predictions = json.dumps(dataset['predictions'])
            response.prediction_dataset = response_dataset
        except Exception as e:
            self.__log.error(f"get_prediction_dataset: Error while reading parameter for prediction dataset {get_prediction_dataset_request.prediction_dataset_identifier} for user {get_prediction_dataset_request.user_identifier}")
            self.__log.error(f"get_prediction_dataset: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Prediction Dataset {get_prediction_dataset_request.prediction_dataset_identifier} for user {get_prediction_dataset_request.user_identifier}")

                
        return response

    def delete_prediction_dataset(
        self, delete_prediction_dataset_request: "DeletePredictionDatasetRequest"
    ) -> "DeletePredictionDatasetResponse":
        """
        Delete a dataset from database and disc
        ---
        Parameter
        1. grpc request object containing the user identifier, dataset identifier
        ---
        Return empty DeleteDatasetResponse object or a GRPC error if ressource NOT_FOUND
        """
        self.__log.debug(f"delete_prediction_dataset: deleting prediction dataset {delete_prediction_dataset_request.prediction_dataset_identifier}, of user {delete_prediction_dataset_request.user_identifier}")
        result = self.__data_storage.delete_prediction_dataset(delete_prediction_dataset_request.user_identifier, delete_prediction_dataset_request.prediction_dataset_identifier)
        self.__log.debug(f"delete_prediction_dataset: {str(result)} prediction datasets deleted")
        return DeletePredictionDatasetResponse()