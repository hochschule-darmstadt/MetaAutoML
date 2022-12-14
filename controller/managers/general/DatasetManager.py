from DataStorage import DataStorage
from ControllerBGRPC import *
import json, logging, os
from CsvManager import CsvManager
from LongitudinalDataManager import LongitudinalDataManager
from DataSetAnalysisManager import DataSetAnalysisManager
from ThreadLock import ThreadLock



class DatasetManager:
    """The DatasetManager provides all functionality related to Datasets objects
    """

    def __init__(self, data_storage: DataStorage, dataset_analysis_lock: ThreadLock) -> None:
        """Initialize a new DatasetManager instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            dataset_analysis_lock (ThreadLock): The dataset analysis lock instance to protect from multiple thread using critical parts of the DatasetAnalysisManager
        """
        self.__data_storage: DataStorage = data_storage
        self.__dataset_analysis_lock = dataset_analysis_lock
        self.__log = logging.getLogger('DatasetManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))

    def create_dataset(
        self, create_dataset_request: "CreateDatasetRequest"
    ) -> "CreateDatasetResponse":
        """Create a new dataset record and start the dataset analysis

        Args:
            create_dataset_request (CreateDatasetRequest): GRPC message holding the user id and dataset informations of the new dataset

        Returns:
            CreateDatasetResponse: The empty GRPC response message
        """
        self.__log.debug(f"create_dataset: saving new dataset {create_dataset_request.dataset_name} for user {create_dataset_request.user_id}, with filename {create_dataset_request.file_name}, with dataset type {create_dataset_request.dataset_type}")
        dataset_id: str = self.__data_storage.create_dataset(create_dataset_request.user_id, create_dataset_request.file_name, create_dataset_request.dataset_type, create_dataset_request.dataset_name, create_dataset_request.encoding)
        self.__log.debug(f"create_dataset: new dataset saved id: {dataset_id}")
        # If the dataset is a certain type the dataset can be analyzed.
        self.__log.debug("create_dataset: executing dataset analysis...")
        dataset_analysis = DataSetAnalysisManager(dataset_id, create_dataset_request.user_id, self.__data_storage, self.__dataset_analysis_lock)
        dataset_analysis.start()
        response = CreateDatasetResponse()
        return response

    def __dataset_object_to_rpc_object(self, user_id: str, dataset: dict) -> Dataset:
        """Convert a dataset record dictionary into the GRPC Dataset object

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            dataset (dict): The retrieved dataset record dictionary

        Raises:
            grpclib.GRPCError: grpclib.Status.UNAVAILABLE, raised when a dictionary field could not be read

        Returns:
            Dataset: The GRPC dataset object generated from the dictonary
        """
        
        backend_frontend_encoding_conversion_table = {
            "ascii": "ascii",
            "utf_8": "utf-8",
            "utf_16": "utf-16",
            "utf_32": "utf-32",
            "cp1252" : "windows-1252",
            "utf-8": "utf-8",
            "utf-16": "utf-16",
            "utf-32": "utf-32",
            "utf-16-le": "utf-16le",
            "utf-16le": "utf-16-le",
            "utf-16be": "utf_16_be", 
            "utf_16_be": "utf-16le",
            "utf_16_be": "utf-16be",
            "latin-1": "latin-1",
            "": ""
        }

        try:
            dataset_detail = Dataset()
            dataset_detail.id = str(dataset["_id"])
            dataset_detail.name = dataset["name"]
            dataset_detail.type = dataset['type']
            dataset_detail.path = dataset["path"]
            if dataset['type'] in [':text', ':tabular', ':time_series', ':time_series_longitudinal']:
                dataset["file_configuration"]["encoding"] = backend_frontend_encoding_conversion_table[dataset["file_configuration"]["encoding"]]
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
        """Get all datasets or get all datasets using an optional filter

        Args:
            get_datasets_request (GetDatasetsRequest): The GRPC request holding the user id and filters

        Returns:
            GetDatasetsResponse: The GRPC response holding the list of found datasets
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
        """Get dataset details for a specific dataset

        Args:
            get_dataset_request (GetDatasetRequest): The GRPC request holding the user id and and dataset id

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if no dataset record was found

        Returns:
            GetDatasetResponse: The GRPC response holding the found dataset
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
        """Get column names for a specific tabular dataset

        Args:
            get_tabular_dataset_column_request (GetTabularDatasetColumnRequest): The GRPC request holding the user and dataset ids

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised when no dataset was found for the requested informations

        Returns:
            GetTabularDatasetColumnResponse: The GRPC response holding the list of columns of a tabular dataset
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
        """Delete a dataset from database and disc

        Args:
            delete_dataset_request (DeleteDatasetRequest): The GRPC request containing the user id, dataset id

        Returns:
            DeleteDatasetResponse: The empty GRPC response
        """
        self.__log.debug(f"delete_dataset: deleting dataset {delete_dataset_request.dataset_id}, of user {delete_dataset_request.user_id}")
        result = self.__data_storage.delete_dataset(delete_dataset_request.user_id, delete_dataset_request.dataset_id)
        self.__log.debug(f"delete_dataset: {str(result)} datasets deleted")
        return DeleteDatasetResponse()

    def set_dataset_file_configuration(
        self,
        set_dataset_file_configuration_request: "SetDatasetFileConfigurationRequest",
    ) -> "SetDatasetFileConfigurationResponse":
        """Persist new dataset file configuration in MongoDB for the dataset

        Args:
            set_dataset_file_configuration_request (SetDatasetFileConfigurationRequest): The GRPC request object containing the user id, dataset id, and new file configuration

        Returns:
            SetDatasetFileConfigurationResponse: The empty GRPC response
        """
        self.__log.debug(f"set_dataset_file_configuration: setting new file configuration new configuration {set_dataset_file_configuration_request.file_configuration}, for dataset {set_dataset_file_configuration_request.dataset_id}, of user {set_dataset_file_configuration_request.user_id}")
        self.__data_storage.update_dataset(set_dataset_file_configuration_request.user_id, set_dataset_file_configuration_request.dataset_id, { "file_configuration": json.loads(set_dataset_file_configuration_request.file_configuration) })
        self.__log.debug(f"set_dataset_file_configuration: executing dataset analysis for dataset: {set_dataset_file_configuration_request.dataset_id} for user {set_dataset_file_configuration_request.user_id}")
        dataset_analysis = DataSetAnalysisManager(set_dataset_file_configuration_request.dataset_id, set_dataset_file_configuration_request.user_id, self.__data_storage, self.__dataset_analysis_lock)
        dataset_analysis.start()
        return SetDatasetFileConfigurationResponse()