from DatasetManager import DatasetManager
from TrainingManager import TrainingManager
from ModelManager import ModelManager
from UserManger import UserManager
from RdfManager import RdfManager
from ControllerBGRPC import *
import multiprocessing, os, logging, asyncio
from JsonUtil import get_config_property
from concurrent.futures.process import ProcessPoolExecutor

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class ControllerServiceManager(ControllerServiceBase):

    def __init__(self, executor: ProcessPoolExecutor):
        self.__log = logging.getLogger('ControllerServiceManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__executor = executor
        self.__loop = asyncio.get_event_loop()
        self.__multiprocessing_manager = multiprocessing.Manager()
        self.__data_storage_lock = self.__multiprocessing_manager.Lock()
        self.__data_storage_dir = os.path.join(ROOT_PATH, get_config_property("datasets-path"))
        if os.getenv("MONGO_DB_DEBUG") == "YES":
            self.__log.info("__init__: Using localhost mongo db")
            self.__mongo_db_url = "mongodb://localhost:27017/"
        elif os.getenv("MONGO_CLUSTER") == "YES":
            self.__log.info("__init__: Using cluster mongo db")
            self.__mongo_db_url = "mongodb://"+os.getenv("MONGODB_SERVICE_HOST")+":"+os.getenv("MONGODB_SERVICE_PORT")+""
        else:
            self.__log.info("__init__: Using docker-compose mongo db")
            self.__mongo_db_url = "mongodb://root:example@mongo"
        super().__init__()
        self.__log.info("__init__: New mongo db client intialized.")

    ####################################
    ## User OPERATIONS
    ####################################
#region

    async def create_new_user(
        self, create_new_user_request: "CreateNewUserRequest"
    ) -> "CreateNewUserResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, UserManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).create_new_user, create_new_user_request
        )
        self.__log.debug("create_new_user: executed")
        return response

    async def get_home_overview_information(
        self, get_home_overview_information_request: "GetHomeOverviewInformationRequest"
    ) -> "GetHomeOverviewInformationResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, UserManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_home_overview_information, get_home_overview_information_request
        )
        self.__log.debug("get_home_overview_information: executed")
        return response


#endregion

    ####################################
    ## DATASET RELATED OPERATIONS
    ####################################
#region 


    async def create_dataset(
        self, create_dataset_request: "CreateDatasetRequest"
    ) -> "CreateDatasetResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, DatasetManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).create_dataset, create_dataset_request
        )
        self.__log.debug("create_dataset: executed")
        return response

    async def get_datasets(
        self, get_datasets_request: "GetDatasetsRequest"
    ) -> "GetDatasetsResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, DatasetManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_datasets, get_datasets_request
        )
        self.__log.debug("get_datasets: executed")
        return response

    async def get_dataset(
        self, get_dataset_request: "GetDatasetRequest"
    ) -> "GetDatasetResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, DatasetManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_dataset, get_dataset_request
        )
        self.__log.debug("get_dataset: executed")
        return response

    async def get_tabular_dataset_column(
        self, get_tabular_dataset_column_request: "GetTabularDatasetColumnRequest"
    ) -> "GetTabularDatasetColumnResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, DatasetManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_tabular_dataset_column, get_tabular_dataset_column_request
        )
        self.__log.debug("get_tabular_dataset_column: executed")
        return response

    async def delete_dataset(
        self, delete_dataset_request: "DeleteDatasetRequest"
    ) -> "DeleteDatasetResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, DatasetManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).delete_dataset, delete_dataset_request
        )
        self.__log.debug("delete_dataset: executed")
        return response

    async def set_dataset_file_configuration(
        self,
        set_dataset_file_configuration_request: "SetDatasetFileConfigurationRequest",
    ) -> "SetDatasetFileConfigurationResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, DatasetManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).set_dataset_file_configuration, set_dataset_file_configuration_request
        )
        self.__log.debug("delete_dataset: set_dataset_file_configuration")
        return response


#endregion

    ####################################
    ## TRAINING RELATED OPERATIONS
    ####################################
#region



    async def create_training(
        self, create_training_request: "CreateTrainingRequest"
    ) -> "CreateTrainingResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, TrainingManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).create_training, create_training_request
        )
        self.__log.debug("create_training: executed")
        return response

    async def get_trainings(
        self, get_trainings_request: "GetTrainingsRequest"
    ) -> "GetTrainingsResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, TrainingManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_trainings, get_trainings_request
        )
        self.__log.debug("get_trainings: executed")
        return response

    async def get_training(
        self, get_training_request: "GetTrainingRequest"
    ) -> "GetTrainingResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, TrainingManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_training, get_training_request
        )
        self.__log.debug("get_training: executed")
        return response

    async def delete_training(
        self, delete_training_request: "DeleteTrainingRequest"
    ) -> "DeleteTrainingResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, TrainingManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).delete_training, delete_training_request
        )
        self.__log.debug("delete_training: executed")
        return response



#endregion

    ####################################
    ## MODEL RELATED OPERATIONS
    ####################################
#region


    async def get_models(
        self, get_models_request: "GetModelsRequest"
    ) -> "GetModelsResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, ModelManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_models, get_models_request
        )
        self.__log.debug("get_models: executed")
        return response

    async def get_model(
        self, get_model_request: "GetModelRequest"
    ) -> "GetModelResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, ModelManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).get_model, get_model_request
        )
        self.__log.debug("get_model: executed")
        return response

    async def model_predict(
        self, model_predict_request: "ModelPredictRequest"
    ) -> "ModelPredictResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, ModelManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).model_predict, model_predict
        )
        self.__log.debug("model_predict: executed")
        return response

    async def delete_model(
        self, delete_model_request: "DeleteModelRequest"
    ) -> "DeleteModelResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, ModelManager(self.__data_storage_dir, self.__mongo_db_url, self.__data_storage_lock).delete_model, delete_model_request
        )
        self.__log.debug("delete_model: executed")
        return response



#endregion

    ####################################
    ## ONTOLOGY RELATED OPERATIONS
    ####################################
#region


    async def get_auto_ml_solutions_for_configuration(
        self,
        get_auto_ml_solutions_for_configuration_request: "GetAutoMlSolutionsForConfigurationRequest",
    ) -> "GetAutoMlSolutionsForConfigurationResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, RdfManager().get_auto_ml_solutions_for_configuration, get_auto_ml_solutions_for_configuration_request
        )
        self.__log.debug("get_auto_ml_solutions_for_configuration: executed")
        return response

    async def get_available_strategies(
        self, get_available_strategies_request: "GetAvailableStrategiesRequest"
    ) -> "GetAvailableStrategiesResponse":
        #TODO add to ontology and RdfManager
        result = GetAvailableStrategiesResponse()
        result.strategies = [
            Strategy(
                'data_preparation.ignore_redundant_features',
                'Ignore redundant features',
                'This strategy ignores certain dataset columns if they have been flagged as duplicate in the dataset analysis.'
            ),
            Strategy(
                'data_preparation.ignore_redundant_samples',
                'Ignore redundant samples',
                'This strategy ignores certain dataset rows if they have been flagged as duplicate in the dataset analysis.'
            ),
            Strategy(
                'data_preparation.split_large_datasets',
                'Split large datasets',
                'This strategy truncates the training data if the time limit is relatively short for the size of the dataset.'
            ),
        ]
        return result

    async def get_dataset_types(
        self, get_dataset_types_request: "GetDatasetTypesRequest"
    ) -> "GetDatasetTypesResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, RdfManager().get_dataset_types, get_dataset_types_request
        )
        self.__log.debug("get_dataset_types: executed")
        return response

    async def get_ml_libraries_for_task(
        self, get_ml_libraries_for_task_request: "GetMlLibrariesForTaskRequest"
    ) -> "GetMlLibrariesForTaskResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, RdfManager().get_ml_libraries_for_task, get_ml_libraries_for_task_request
        )
        self.__log.debug("get_ml_libraries_for_task: executed")
        return response

    async def get_objects_information(
        self, get_objects_information_request: "GetObjectsInformationRequest"
    ) -> "GetObjectsInformationResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, RdfManager().get_objects_information, get_objects_information_request
        )
        self.__log.debug("get_objects_information: executed")
        return response

    async def get_tasks_for_dataset_type(
        self, get_tasks_for_dataset_type_request: "GetTasksForDatasetTypeRequest"
    ) -> "GetTasksForDatasetTypeResponse":
        response = await self.__loop.run_in_executor(
            self.__executor, RdfManager().get_tasks_for_dataset_type, get_tasks_for_dataset_type_request
        )
        self.__log.debug("get_tasks_for_dataset_type: executed")
        return response


#endregion