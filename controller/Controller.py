import os
import logging
from ssl import SSLContext
import ssl

from Controller_bgrpc import *
from grpclib.server import Server
import asyncio

from JsonUtil import get_config_property
from ControllerManager import ControllerManager
from persistence.data_storage import DataStorage


def _load_credential_from_file(filepath):
    """
    Load the certificate from disk
    ---
    Parameter
    1. path to certificate to read
    ---
    Return the certificate str
    """
    real_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(real_path, 'rb') as f:
        return f.read()


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

SERVER_CERTIFICATE = _load_credential_from_file('certificate/server.crt')
SERVER_CERTIFICATE_KEY = _load_credential_from_file('certificate/server.key')


class ControllerService(ControllerServiceBase):
    """includes all gRPC functions available for the client frontend"""

    def __init__(self):
        # init data storage
        data_storage_dir = os.path.join(ROOT_PATH, get_config_property("datasets-path"))
        if os.getenv("MONGO_DB_DEBUG") == "YES":
            data_storage = DataStorage(data_storage_dir, "mongodb://localhost:27017/")
        elif os.getenv("MONGO_CLUSTER") == "YES":
            data_storage = DataStorage(data_storage_dir, "mongodb://"+os.getenv("MONGODB_SERVICE_HOST")+":"+os.getenv("MONGODB_SERVICE_PORT")+"")
        else:
            data_storage = DataStorage(data_storage_dir)
        self._controllerManager = ControllerManager(data_storage)

    async def create_new_user(self) -> "CreateNewUserResponse":
        """ Return a new OMA-ML user id. """
        request = CreateNewUserRequest()
        response = self._controllerManager.CreateNewUser(request)
        return response

    async def get_auto_ml_model(
        self, username: str, training_id: str, auto_ml: str
    ) -> "GetAutoMlModelResponse":
        """ return the generated model as a .zip for one AutoML by its Training id."""
        request = GetAutoMlModelRequest(username, training_id, auto_ml)
        response = self._controllerManager.GetAutoMlModel(request)
        return response

    async def get_compatible_auto_ml_solutions(
        self, username: str, configuration: Dict[str, str]
    ) -> "GetCompatibleAutoMlSolutionsResponse":
        """return a list of AutoML solutions compatible with the current configuration
        """
        request = GetCompatibleAutoMlSolutionsRequest(username, configuration)
        response = self._controllerManager.GetCompatibleAUtoMlSolutions(request)
        return response

    async def get_dataset_types(self) -> "GetDatasetTypesResponse":
        """return all dataset types."""
        request = GetDatasetTypesRequest()
        response = self._controllerManager.GetDatasetTypes(request)
        return response

    async def get_datasets(
        self, username: str, type: "DatasetType"
    ) -> "GetDatasetsResponse":
        """return all datasets of a specific type."""
        request = GetDatasetsRequest(username, type)
        datasets = self._controllerManager.GetDatasets(request)
        return datasets

    async def get_dataset(self, username: str, identifier: str) -> "GetDatasetResponse":
        """
        returns details of a specified dataset.

        The result is a list of TableColumns containing:
        name: the name of the dataset
        datatype: the datatype of the column
        firstEntries: the first couple of rows of the dataset
        """
        request = GetDatasetRequest(username, identifier)
        response = self._controllerManager.GetDataset(request)
        return response

    async def get_trainings(self, username: str) -> "GetTrainingsResponse":
        """return a list of all Trainings the controller has knowledge of. """
        request = GetTrainingsRequest(username)
        response = self._controllerManager.GetTrainings(request)
        return response

    async def get_training(self, username: str, id: str) -> "GetTrainingResponse":
        """return the status of a specific Training. The result is a Training status and a list of the automl output and its status."""
        request = GetTrainingRequest(username, id)
        response = self._controllerManager.GetTraining(request)
        return response

    async def get_all_trainings(self, username: str) -> "GetAllTrainingsResponse":
        """return all existing trainings for a user"""
        request = GetAllTrainingsRequest(username)
        response = self._controllerManager.GetAllTrainings(request)
        return response

    async def get_supported_ml_libraries(
        self, username: str, task: str
    ) -> "GetSupportedMlLibrariesResponse":
        """return all supported machine learning libraries for a specific task (by searching supported AutoML)
        """
        request = GetSupportedMlLibrariesRequest(username, task)
        response = self._controllerManager.GetSupportedMlLibraries(request)
        return response

    async def get_tabular_dataset_column(
        self, username: str, dataset_identifier: str
    ) -> "GetTabularDatasetColumnResponse":
        """return all the column names of a tabular dataset."""
        request = GetTabularDatasetColumnRequest(username, dataset_identifier)
        response = self._controllerManager.GetTabularDatasetColumn(request)
        return response

    async def get_dataset_compatible_tasks(
        self, username: str, dataset_name: str
    ) -> "GetDatasetCompatibleTasksResponse":
        """return all supported AutoML tasks."""
        request = GetDatasetCompatibleTasksRequest(username, dataset_name)
        response = self._controllerManager.GetDatasetCompatibleTasks(request)
        return response

    async def get_models(
        self, username: str, dataset_id: str, top3: bool
    ) -> "GetModelsResponse":
        """return all models for a given dataset, with option to only return top 3"""
        request = GetModelsRequest(username, dataset_id, top3)
        response = self._controllerManager.GetModels(request)
        return response

    async def get_model(self, username: str, model_id: str) -> "GetModelResponse":
        """return model for a given id"""
        request = GetModelRequest(username, model_id)
        response = self._controllerManager.GetModel(request)
        return response

    async def get_objects_information(
        self, ids: Optional[List[str]]
    ) -> "GetObjectsInformationResponse":
        """return all information fields of an object"""
        request = GetObjectsInformationRequest(ids)
        response = self._controllerManager.GetObjectsInformation(request)
        return response

    async def get_home_overview_information(
        self, user: str
    ) -> "GetHomeOverviewInformationResponse":
        """return overview information for home page"""
        request = GetHomeOverviewInformationRequest(user)
        response = self._controllerManager.GetHomeOverviewInformation(request)
        return response

    async def upload_dataset_file(
        self, username: str, file_name: str, dataset_name: str, type: str
    ) -> "UploadDatasetFileResponse":
        """upload a new dataset file as bytes to the controller repository."""
        request = UploadDatasetFileRequest(username, file_name, dataset_name, type)
        response = self._controllerManager.UploadNewDataset(request)
        return response

    async def set_dataset_configuration(
        self, username: str, identifier: str, file_configuration: str
    ) -> "SetDatasetConfigurationResponse":
        """persist new dataset configuration"""
        request = SetDatasetConfigurationRequest(username, identifier, file_configuration)
        response = self._controllerManager.SetDatasetConfiguration(request)
        return response

    async def start_auto_ml_process(
        self,
        username: str,
        dataset: str,
        task: str,
        configuration: str,
        required_auto_mls: Optional[List[str]],
        runtime_constraints: str,
        dataset_configuration: str,
        test_configuration: str,
        file_configuration: str,
        metric: str,
        required_libraries: Optional[List[str]],
    ) -> "StartAutoMlProcessResponse":
        """start a new AutoML run, using the provided configuration."""
        request = StartAutoMlProcessRequest(
            username,
            dataset,
            task,
            configuration,
            required_auto_mls,
            runtime_constraints,
            dataset_configuration,
            test_configuration,
            file_configuration,
            metric,
            required_libraries,
        )
        response = self._controllerManager.StartAutoMLProcess(request)
        return response

    async def test_auto_ml(
        self, username: str, test_data: bytes, model_id: str
    ) -> "TestAutoMlResponse":
        """start a new AutoML run, using the provided configuration."""
        request = TestAutoMlRequest(username, test_data, model_id)
        response = self._controllerManager.TestAutoML(request)
        return response


def create_secure_context() -> SSLContext:
    """
    Create the required SSL context for inbound Better GRPC connections
    ---
    Return the SSL Context for inbound connections
    """
    #Credit: https://github.com/vmagamedov/grpclib/blob/master/examples/mtls/server.py
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_cert_chain(str("certificate/server.crt"), str('certificate/server.key'))
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20')
    ctx.set_alpn_protocols(['h2'])
    try:
        ctx.set_npn_protocols(['h2'])
    except NotImplementedError:
        pass
    return ctx

async def main():
    server = Server([ControllerService()])
    context = SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(certfile="certificate/server.crt", keyfile='certificate/server.key')
    await server.start(get_config_property('controller-server-adress'), get_config_property('controller-server-port'), ssl=create_secure_context())
    await server.wait_closed()


if __name__ == '__main__':

    logging.basicConfig()
    #serve()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('done.')
