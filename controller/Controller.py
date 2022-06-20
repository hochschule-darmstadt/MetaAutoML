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
        else:
            data_storage = DataStorage(data_storage_dir)
        self._controllerManager = ControllerManager(data_storage)

    async def get_auto_ml_model(
        self, get_auto_ml_model_request: "GetAutoMlModelRequest"
    ) -> "GetAutoMlModelResponse":
        """ return the generated model as a .zip for one AutoML by its session id."""
        response = self._controllerManager.GetAutoMlModel(get_auto_ml_model_request)
        return response

    async def get_compatible_auto_ml_solutions(
        self,
        get_compatible_auto_ml_solutions_request: "GetCompatibleAutoMlSolutionsRequest",
    ) -> "GetCompatibleAutoMlSolutionsResponse":
        """return a list of AutoML solutions compatible with the current configuration
        """
        response = self._controllerManager.GetCompatibleAUtoMlSolutions(get_compatible_auto_ml_solutions_request)
        return response

    async def get_datasets(
        self, get_datasets_request: "GetDatasetsRequest"
    ) -> "GetDatasetsResponse":
        """return all datasets of a specific type."""
        datasets = self._controllerManager.GetDatasets(get_datasets_request)
        return datasets

    async def get_dataset(
        self, get_dataset_request: "GetDatasetRequest"
    ) -> "GetDatasetResponse":
        """
        returns details of a specified dataset.

        The result is a list of TableColumns containing:
        name: the name of the dataset
        datatype: the datatype of the column
        firstEntries: the first couple of rows of the dataset
        """
        response = self._controllerManager.GetDataset(get_dataset_request)
        return response

    async def get_sessions(
        self, get_sessions_request: "GetSessionsRequest"
    ) -> "GetSessionsResponse":
        """return a list of all sessions the controller has knowledge of. """
        response = self._controllerManager.GetSessions(get_sessions_request)
        return response

    async def get_session_status(
        self, get_session_status_request: "GetSessionStatusRequest"
    ) -> "GetSessionStatusResponse":
        """return the status of a specific session. The result is a session status and a list of the automl output and its status."""
        response = self._controllerManager.GetSessionStatus(get_session_status_request)
        return response

    async def get_supported_ml_libraries(
        self, get_supported_ml_libraries_request: "GetSupportedMlLibrariesRequest"
    ) -> "GetSupportedMlLibrariesResponse":
        """return all supported machine learning libraries for a specific task (by searching supported AutoML)
        """
        response = self._controllerManager.GetSupportedMlLibraries(get_supported_ml_libraries_request)
        return response

    async def get_tabular_dataset_column_names(
        self,
        get_tabular_dataset_column_names_request: "GetTabularDatasetColumnNamesRequest",
    ) -> "GetTabularDatasetColumnNamesResponse":
        """return all the column names of a tabular dataset."""
        response = self._controllerManager.GetTabularDatasetColumnNames(get_tabular_dataset_column_names_request)
        return response

    async def get_dataset_compatible_tasks(
        self, get_dataset_compatible_tasks_request: "GetDatasetCompatibleTasksRequest"
    ) -> "GetDatasetCompatibleTasksResponse":
        """return all supported AutoML tasks."""
        response = self._controllerManager.GetDatasetCompatibleTasks(get_dataset_compatible_tasks_request)
        return response

    async def upload_dataset_file(
        self, upload_dataset_file_request: "UploadDatasetFileRequest"
    ) -> "UploadDatasetFileResponse":
        """upload a new dataset file as bytes to the controller repository."""
        response = self._controllerManager.UploadNewDataset(upload_dataset_file_request)
        return response

    async def start_auto_ml_process(
        self, start_auto_ml_process_request: "StartAutoMlProcessRequest"
    ) -> "StartAutoMlProcessResponse":
        """start a new AutoML run, using the provided configuration."""
        response = self._controllerManager.StartAutoMLProcess(start_auto_ml_process_request)
        return response

    async def test_auto_ml(
        self, test_auto_ml_request: "TestAutoMlRequest"
    ) -> "TestAutoMlResponse":
        """start a new AutoML run, using the provided configuration."""
        response = self._controllerManager.TestAutoML(test_auto_ml_request)
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
    await server.start("127.0.0.1", get_config_property('controller-server-port'), ssl=create_secure_context())
    await server.wait_closed()


if __name__ == '__main__':
    logging.basicConfig()
    #serve()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('done.')
