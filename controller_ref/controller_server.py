import os
from JsonUtil import get_config_property
from concurrent.futures.process import ProcessPoolExecutor
from grpclib.server import Server
from ssl import SSLContext
import ssl
import logging
import asyncio
from controller_bgrpc import *
import multiprocessing

from general.DatasetManager import DatasetManager

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

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

SERVER_CERTIFICATE = _load_credential_from_file('certificate/server.crt')
SERVER_CERTIFICATE_KEY = _load_credential_from_file('certificate/server.key')


class ControllerService(ControllerServiceBase):

    def __init__(self, executor: ProcessPoolExecutor):
        self.__log = logging.getLogger('ControllerService')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__executor = executor
        self.__loop = asyncio.get_event_loop()
        self.__multiprocessing_manager = multiprocessing.Manager()
        self.__data_storage_lock = self.__multiprocessing_manager.Lock()
        self.__data_storage_dir = os.path.join(ROOT_PATH, get_config_property("datasets-path"))
        if os.getenv("MONGO_DB_DEBUG") == "YES":
            self.__log.info("Using localhost mongo db")
            self.__mongo_db_url = "mongodb://localhost:27017/"
        elif os.getenv("MONGO_CLUSTER") == "YES":
            self.__log.info("Using cluster mongo db")
            self.__mongo_db_url = "mongodb://"+os.getenv("MONGODB_SERVICE_HOST")+":"+os.getenv("MONGODB_SERVICE_PORT")+""
        else:
            self.__log.info("Using docker-compose mongo db")
            self.__mongo_db_url = "mongodb://root:example@mongo"
        super().__init__()
        self.__log.info("New mongo db client intialized.")

    async def create_new_user(
        self, create_new_user_request: "CreateNewUserRequest"
    ) -> "CreateNewUserResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_objects_information(
        self, get_objects_information_request: "GetObjectsInformationRequest"
    ) -> "GetObjectsInformationResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_home_overview_information(
        self, get_home_overview_information_request: "GetHomeOverviewInformationRequest"
    ) -> "GetHomeOverviewInformationResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)




    async def create_dataset(
        self, create_dataset_request: "CreateDatasetRequest"
    ) -> "CreateDatasetResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_dataset_types(
        self, get_dataset_types_request: "GetDatasetTypesRequest"
    ) -> "GetDatasetTypesResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_datasets(
        self, get_datasets_request: "GetDatasetsRequest"
    ) -> "GetDatasetsResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, DatasetManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_datasets, get_datasets_request
        )
        self.__log.debug("get_datasets: ")
        return response

    async def get_dataset(
        self, get_dataset_request: "GetDatasetRequest"
    ) -> "GetDatasetResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_tabular_dataset_column(
        self, get_tabular_dataset_column_request: "GetTabularDatasetColumnRequest"
    ) -> "GetTabularDatasetColumnResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def delete_dataset(
        self, delete_dataset_request: "DeleteDatasetRequest"
    ) -> "DeleteDatasetResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def set_dataset_file_configuration(
        self,
        set_dataset_file_configuration_request: "SetDatasetFileConfigurationRequest",
    ) -> "SetDatasetFileConfigurationResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)





    async def create_training(
        self, create_training_request: "CreateTrainingRequest"
    ) -> "CreateTrainingResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_trainings(
        self, get_trainings_request: "GetTrainingsRequest"
    ) -> "GetTrainingsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_training(
        self, get_training_request: "GetTrainingRequest"
    ) -> "GetTrainingResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def delete_training(
        self, delete_training_request: "DeleteTrainingRequest"
    ) -> "DeleteTrainingResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)





    async def get_models(
        self, get_models_request: "GetModelsRequest"
    ) -> "GetModelsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_model(
        self, get_model_request: "GetModelRequest"
    ) -> "GetModelResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def model_predict(
        self, model_predict_request: "ModelPredictRequest"
    ) -> "ModelPredictResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def delete_model(
        self, delete_model_request: "DeleteModelRequest"
    ) -> "DeleteModelResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)





    async def get_auto_ml_solutions_for_configuration(
        self,
        get_auto_ml_solutions_for_configuration_request: "GetAutoMlSolutionsForConfigurationRequest",
    ) -> "GetAutoMlSolutionsForConfigurationResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_available_strategies(
        self, get_available_strategies_request: "GetAvailableStrategiesRequest"
    ) -> "GetAvailableStrategiesResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_ml_libraries_for_task(
        self, get_ml_libraries_for_task_request: "GetMlLibrariesForTaskRequest"
    ) -> "GetMlLibrariesForTaskResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_tasks_for_dataset_type(
        self, get_tasks_for_dataset_type_request: "GetTasksForDatasetTypeRequest"
    ) -> "GetTasksForDatasetTypeResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)



async def main():
    with ProcessPoolExecutor(max_workers=4) as executor:
        server = Server([ControllerService(executor)])
        context = SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(certfile="certificate/server.crt", keyfile='certificate/server.key')
        await server.start(get_config_property('controller-server-adress'), get_config_property('controller-server-port'), ssl=create_secure_context())
        await server.wait_closed()


if __name__ == '__main__':
    logging.basicConfig()
    print("controller started")
    asyncio.run(main())
    print('done.')
