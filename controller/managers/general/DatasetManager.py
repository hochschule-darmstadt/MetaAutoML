from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import json, logging, os
from CsvManager import CsvManager
from LongitudinalDataManager import LongitudinalDataManager

class DatasetManager:

    def __init__(self, data_storage: DataStorage) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('DatasetManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))

    def create_dataset(
        self, create_dataset_request: "CreateDatasetRequest"
    ) -> "CreateDatasetResponse":
        """
        Upload a new dataset
        ---
        Parameter
        1. dataset information
        ---
        Return empty CreateDatasetResponse object
        """
        self.__log.debug(f"create_dataset: saving new dataset {create_dataset_request.dataset_name} for user {create_dataset_request.user_id}, with filename {create_dataset_request.file_name}, with dataset type {create_dataset_request.dataset_type}")
        dataset_id: str = self.__data_storage.create_dataset(create_dataset_request.user_id, create_dataset_request.file_name, create_dataset_request.dataset_type, create_dataset_request.dataset_name)
        self.__log.debug(f"create_dataset: new dataset saved id: {dataset_id}")
        response = CreateDatasetResponse()
        return response

    def __dataset_object_to_rpc_object(self, user_id, dataset):
        try:
            dataset_detail = Dataset()
            dataset_detail.id = str(dataset["_id"])
            dataset_detail.name = dataset["name"]
            dataset_detail.type = dataset['type']
            dataset_detail.path = dataset["path"]
            dataset_detail.file_configuration = json.dumps(dataset["file_configuration"])
            dataset_detail.training_ids = dataset['training_ids']
            dataset_detail.analysis = json.dumps(dataset['analysis'])
            return dataset_detail
        except Exception as e:
            self.__log.error(f"__dataset_object_to_rpc_object: Error while reading parameter for dataset {str(dataset['_id'])} for user {user_id}")
            self.__log.error(f"__dataset_object_to_rpc_object: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Dataset {str(dataset['_id'])} for user {user_id}")



    def get_datasets(
        self, get_datasets_request: "GetDatasetsRequest"
    ) -> "GetDatasetsResponse":
        """
        Get all datasets for a specific task
        ---
        Parameter
        1. grpc request object, containing the user id
        ---
        Return a list of compatible datasets or a GRPC error UNAVAILABLE for read errors
        """
        response = GetDatasetsResponse()
        self.__log.debug(f"get_datasets: get all datasets for user {get_datasets_request.user_id}")
        all_datasets: list[dict[str, object]] = self.__data_storage.get_datasets(get_datasets_request.user_id)
        
        self.__log.debug(f"get_datasets: found {all_datasets.count} datasets for user {get_datasets_request.user_id}")
        for dataset in all_datasets:
            response.datasets.append(self.__dataset_object_to_rpc_object(get_datasets_request.user_id, dataset))
        return response

    def get_dataset(
        self, get_dataset_request: "GetDatasetRequest"
    ) -> "GetDatasetResponse":
        """
        Get dataset details for a specific dataset
        ---
        Parameter
        1. grpc request object, containing the user, and dataset id
        ---
        Return dataset details
        The result is a GetDatasetResponse object describing one dataset or a GRPC error if ressource NOT_FOUND or UNAVAILABLE for read errors
        """
        response = GetDatasetResponse()
        self.__log.debug(f"get_datasets: trying to get dataset {get_dataset_request.dataset_id} for user {get_dataset_request.user_id}")
        found, dataset = self.__data_storage.get_dataset(get_dataset_request.user_id, get_dataset_request.dataset_id)
        if not found:
            self.__log.error(f"get_datasets: dataset {get_dataset_request.dataset_id} for user {get_dataset_request.user_id} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {get_dataset_request.dataset_id} for user {get_dataset_request.user_id} not found, already deleted?")

        response.dataset = self.__dataset_object_to_rpc_object(get_dataset_request.user_id, dataset)
        return response

    def get_tabular_dataset_column(
        self, get_tabular_dataset_column_request: "GetTabularDatasetColumnRequest"
    ) -> "GetTabularDatasetColumnResponse":
        """
        Get column names for a specific tabular dataset
        ---
        Parameter
        1. grpc object containing the user and dataset ids
        ---
        Return list of column names or a GRPC error if ressource NOT_FOUND
        """
        found, dataset = self.__data_storage.get_dataset(get_tabular_dataset_column_request.user_id, get_tabular_dataset_column_request.dataset_id)
        if not found:
            self.__log.error(f"get_tabular_dataset_column: dataset {get_tabular_dataset_column_request.dataset_id} for user {get_tabular_dataset_column_request.user_id} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {get_tabular_dataset_column_request.dataset_id} for user {get_tabular_dataset_column_request.user_id} not found, wrong id?")

        if dataset["type"] == ":tabular" or dataset["type"] == ":time_series" or dataset["type"] == ":text":
            self.__log.debug(f"get_tabular_dataset_column: dataset {get_tabular_dataset_column_request.dataset_id} for user {get_tabular_dataset_column_request.user_id} has CSV type, using CSVManager")
            return CsvManager.get_columns(dataset["path"], dataset["file_configuration"])
        elif dataset["type"] == ":time_series_longitudinal":
            self.__log.debug(f"get_tabular_dataset_column: dataset {get_tabular_dataset_column_request.dataset_id} for user {get_tabular_dataset_column_request.user_id} has TS type, using LongitudinalDataManager")
            return LongitudinalDataManager.read_dimension_names(dataset["path"])

    def delete_dataset(
        self, delete_dataset_request: "DeleteDatasetRequest"
    ) -> "DeleteDatasetResponse":
        """
        Delete a dataset from database and disc
        ---
        Parameter
        1. grpc request object containing the user id, dataset id
        ---
        Return empty DeleteDatasetResponse object or a GRPC error if ressource NOT_FOUND
        """
        self.__log.debug(f"delete_dataset: deleting dataset {delete_dataset_request.dataset_id}, of user {delete_dataset_request.user_id}")
        result = self.__data_storage.delete_dataset(delete_dataset_request.user_id, delete_dataset_request.dataset_id)
        self.__log.debug(f"delete_dataset: {str(result)} datasets deleted")
        return DeleteDatasetResponse()

    def set_dataset_file_configuration(
        self,
        set_dataset_file_configuration_request: "SetDatasetFileConfigurationRequest",
    ) -> "SetDatasetFileConfigurationResponse":
        """
        Persist new dataset file configuration in db
        ---
        Parameter
        1. grpc request object containing the user id, dataset id, and new file configuration
        ---
        Return empty SetDatasetFileConfigurationResponse object or a GRPC error if ressource NOT_FOUND
        """
        self.__log.debug(f"set_dataset_file_configuration: setting new file configuration new configuration {set_dataset_file_configuration_request.file_configuration}, for dataset {set_dataset_file_configuration_request.dataset_id}, of user {set_dataset_file_configuration_request.user_id}")
        self.__data_storage.update_dataset(set_dataset_file_configuration_request.user_id, set_dataset_file_configuration_request.dataset_id, { "file_configuration": set_dataset_file_configuration_request.file_configuration }, True)
        return SetDatasetFileConfigurationResponse()