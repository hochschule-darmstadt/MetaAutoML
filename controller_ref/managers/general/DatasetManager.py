import threading
from DataStorage import DataStorage
from controller_bgrpc import *
from DataStorage import DataStorage
import json, logging, os

class DatasetManager:

    def __init__(self, storage_dir: str, mongo_db_url: str, storage_lock: threading.Lock) -> None:
        self.__data_storage: DataStorage = DataStorage(storage_dir, storage_lock, mongo_db_url)
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
        Return upload status
        """
        # NOTE: dataset fields mixed up (bug in dummy)
        #dataset.file_name = dataset.content.decode("utf-8")
        #dataset.content = bytes(dataset.username, "ascii")
        #dataset.username = "User"


        dataset_id: str = self.__data_storage.InsertDataset(dataset.username, dataset.file_name, dataset.type, dataset.dataset_name)
        print(f"saved new dataset: {dataset_id}")
        
        response = UploadDatasetFileResponse()
        response.return_code = 0
        return response

    def get_dataset_types(
        self, get_dataset_types_request: "GetDatasetTypesRequest"
    ) -> "GetDatasetTypesResponse":
        """
        Get all dataset types
        ---
        Return list of all dataset types
        """
        return self.__rdfManager.GetDatasetTypes(request)

    def get_datasets(
        self, get_datasets_request: "GetDatasetsRequest"
    ) -> "GetDatasetsResponse":
        """
        Get all datasets for a specific task
        ---
        Parameter
        1. TODO add parameter for session object
        ---
        Return a list of compatible datasets
        """
        response = GetDatasetsResponse()
        all_datasets: list[dict[str, object]] = self.__data_storage.get_datasets(get_datasets_request.user_identifier)
        
        for dataset in all_datasets:
            try:
                response_dataset = Dataset()
                
                response_dataset.analysis = json.dumps(dataset['analysis'])
                response_dataset.size = dataset['size']
                response_dataset.identifier = str(dataset["_id"])
                response_dataset.name = dataset["name"]
                response_dataset.type = dataset['type']
                response_dataset.creation_date = datetime.fromtimestamp(int(dataset["mtime"]))
                response_dataset.file_configuration = dataset["file_configuration"]
                response.dataset.append(response_dataset)
            except Exception as e:
                print(f"exception: {e}")
                
        return response

    def get_dataset(
        self, get_dataset_request: "GetDatasetRequest"
    ) -> "GetDatasetResponse":
        """
        Get dataset details for a specific dataset
        ---
        Parameter
        1. dataset identifier
        ---
        Return dataset details
        The result is a list of TableColumns containing:
        name: the name of the dataset
        datatype: the datatype of the column
        firstEntries: the first couple of rows of the dataset
        """
        response = GetDatasetResponse()
        found, dataset = self.__data_storage.GetDataset(get_dataset_request.user_identifier, get_dataset_request.dataset_identifier)
        
        try:
            response_dataset = Dataset()
            response_dataset.analysis = json.dumps(dataset['analysis'])
            response_dataset.size = dataset['size']
            response_dataset.identifier = str(dataset["_id"])
            response_dataset.name = dataset["name"]
            response_dataset.type = dataset['type']
            response_dataset.creation_date = datetime.fromtimestamp(int(dataset["mtime"]))
            response_dataset.file_name = dataset["file_name"]
            response_dataset.file_configuration = dataset["file_configuration"]
            response.dataset_infos = response_dataset
        except Exception as e:
            print(f"exception: {e}")
                
        return response

    def get_tabular_dataset_column(
        self, get_tabular_dataset_column_request: "GetTabularDatasetColumnRequest"
    ) -> "GetTabularDatasetColumnResponse":
        """
        Get column names for a specific tabular dataset
        ---
        Parameter
        1. dataset name
        ---
        Return list of column names
        """
        found, dataset = self.__data_storage.GetDataset(request.username, request.dataset_identifier)
        if not found:
            # no dataset found -> return empty response
            return GetTabularDatasetColumnResponse()

        if dataset["type"] == ":tabular" or dataset["type"] == ":time_series" or dataset["type"] == ":text":
            return CsvManager.GetColumns(dataset["path"], json.loads(dataset["file_configuration"]))
        elif dataset["type"] == ":time_series_longitudinal":
            return LongitudinalDataManager.read_dimension_names(dataset["path"])

    def delete_dataset(
        self, delete_dataset_request: "DeleteDatasetRequest"
    ) -> "DeleteDatasetResponse":
        result = self.__data_storage.delete_dataset(delete_dataset_request.user_identifier, delete_dataset_request.dataset_identifier)
        print(str(result) + " datasets deleted")
        return DeleteDatasetResponse(result)

    def set_dataset_file_configuration(
        self,
        set_dataset_file_configuration_request: "SetDatasetFileConfigurationRequest",
    ) -> "SetDatasetFileConfigurationResponse":
        """
        Persist new dataset configuration in db
        ---
        Parameter
        1. dataset configuration
        ---
        Return
        """
        #self.__data_storage.UpdateDataset(request.username, request.identifier, { "file_configuration": request.file_configuration }, True)
        self.__data_storage.create_dataset(username, identifier, { "file_configuration": file_configuration }, True)
        return SetDatasetFileConfigurationResponse()