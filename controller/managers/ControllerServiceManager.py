from urllib import response
from Container import Application
from DatasetManager import DatasetManager
from PredictionManager import PredictionManager
from ThreadLock import ThreadLock
from TrainingManager import TrainingManager
from ModelManager import ModelManager
from UserManager import UserManager
from OntologyManager import OntologyManager
from ControllerBGRPC import *
import multiprocessing, os, logging, asyncio
from JsonUtil import get_config_property
from concurrent.futures.process import ProcessPoolExecutor
from dependency_injector.wiring import inject, Provide
from MeasureDuration import MeasureDuration
from DataStorage import DataStorage

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class ControllerServiceManager(ControllerServiceBase):
    """Service class that implements GRPC controller interface, all inbound calls are received within this class.

    Args:
        ControllerServiceBase (ControllerServiceBase): Automatically generated GRPC server stub base class
    """

    def __init__(self, executor: ProcessPoolExecutor=None):
        self.__log = logging.getLogger('ControllerServiceManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__executor = executor
        self.__loop = asyncio.get_event_loop()
        super().__init__()
        self.__log.info("__init__: New Controller Service Manager intialized.")

    ####################################
    ## User OPERATIONS
    ####################################
#region

    @inject
    async def create_new_user(
        self, create_new_user_request: "CreateNewUserRequest",
        user_manager: UserManager=Provide[Application.managers.user_manager]
    ) -> "CreateNewUserResponse":
        with MeasureDuration() as m:
            response = user_manager.create_new_user(create_new_user_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, user_manager.create_new_user, create_new_user_request
        #)
        self.__log.warn("create_new_user: executed")
        return response

    @inject
    async def get_home_overview_information(
        self, get_home_overview_information_request: "GetHomeOverviewInformationRequest",
        user_manager: UserManager=Provide[Application.managers.user_manager]
    ) -> "GetHomeOverviewInformationResponse":
        with MeasureDuration() as m:
            response = user_manager.get_home_overview_information(get_home_overview_information_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, user_manager.get_home_overview_information, get_home_overview_information_request
        #)
        self.__log.warn("get_home_overview_information: executed")
        return response


#endregion

    ####################################
    ## DATASET RELATED OPERATIONS
    ####################################
#region

    @inject
    async def create_dataset(
        self, create_dataset_request: "CreateDatasetRequest",
        dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
    ) -> "CreateDatasetResponse":
        with MeasureDuration() as m:
            response = dataset_manager.create_dataset(create_dataset_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, dataset_manager.create_dataset, create_dataset_request
        #)
        self.__log.warn("create_dataset: executed")
        return response

    @inject
    async def get_datasets(
        self, get_datasets_request: "GetDatasetsRequest",
        dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
    ) -> "GetDatasetsResponse":
        with MeasureDuration() as m:
            response = dataset_manager.get_datasets(get_datasets_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, dataset_manager.get_datasets, get_datasets_request
        #)
        self.__log.warn("get_datasets: executed")
        return response

    @inject
    async def get_dataset(
        self, get_dataset_request: "GetDatasetRequest",
        dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
    ) -> "GetDatasetResponse":
        with MeasureDuration() as m:
            response = dataset_manager.get_dataset(get_dataset_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, dataset_manager.get_dataset, get_dataset_request
        #)
        self.__log.warn("get_dataset: executed")
        return response


    @inject
    async def delete_dataset(
        self, delete_dataset_request: "DeleteDatasetRequest",
        dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
    ) -> "DeleteDatasetResponse":
        with MeasureDuration() as m:
            response = dataset_manager.delete_dataset(delete_dataset_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, dataset_manager.delete_dataset, delete_dataset_request
        #)
        self.__log.warn("delete_dataset: executed")
        return response

    @inject
    async def set_dataset_configuration(
        self,
        set_dataset_file_configuration_request: "SetDatasetConfigurationRequest",
        dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
    ) -> "SetDatasetConfigurationResponse":
        with MeasureDuration() as m:
            response = dataset_manager.set_dataset_file_configuration(set_dataset_file_configuration_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, dataset_manager.set_dataset_file_configuration, set_dataset_file_configuration_request
        #)
        self.__log.warn("delete_dataset: set_dataset_file_configuration")
        return response


    @inject
    async def set_dataset_column_schema_configuration(
        self,
        set_dataset_column_schema_configuration_request: "SetDatasetColumnSchemaConfigurationRequest",
        dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
    ) -> "SetDatasetColumnSchemaConfigurationResponse":
        with MeasureDuration() as m:
            response = dataset_manager.set_dataset_column_schema_configuration(set_dataset_column_schema_configuration_request)
        return response

#endregion

    ####################################
    ## TRAINING RELATED OPERATIONS
    ####################################
#region



    @inject
    async def create_training(
        self, create_training_request: CreateTrainingRequest,
        training_manager: TrainingManager=Provide[Application.managers.training_manager]
    ) -> CreateTrainingResponse:
        with MeasureDuration() as m:
            response = await training_manager.create_training(create_training_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, training_manager.create_training, create_training_request
        #)
        self.__log.warn("create_training: executed")
        return response

    @inject
    async def get_trainings(
        self, get_trainings_request: "GetTrainingsRequest",
        training_manager: TrainingManager=Provide[Application.managers.training_manager]
    ) -> "GetTrainingsResponse":
        with MeasureDuration() as m:
            response = training_manager.get_trainings(get_trainings_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, training_manager.get_trainings, get_trainings_request
        #)
        self.__log.warn("get_trainings: executed")
        return response

    @inject
    async def get_training(
        self, get_training_request: "GetTrainingRequest",
        training_manager: TrainingManager=Provide[Application.managers.training_manager]
    ) -> "GetTrainingResponse":
        with MeasureDuration() as m:
            response = training_manager.get_training(get_training_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, training_manager.get_training, get_training_request
        #)
        self.__log.warn("get_training: executed")
        return response

    @inject
    async def delete_training(
        self, delete_training_request: "DeleteTrainingRequest",
        training_manager: TrainingManager=Provide[Application.managers.training_manager]
    ) -> "DeleteTrainingResponse":
        with MeasureDuration() as m:
            response = training_manager.delete_training(delete_training_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, training_manager.delete_training, delete_training_request
        #)
        self.__log.warn("delete_training: executed")
        return response



#endregion

    ####################################
    ## MODEL RELATED OPERATIONS
    ####################################
#region

    @inject
    async def get_models(
        self, get_models_request: "GetModelsRequest",
        model_manager: ModelManager=Provide[Application.managers.model_manager]
    ) -> "GetModelsResponse":
        with MeasureDuration() as m:
            response = model_manager.get_models(get_models_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, model_manager.get_models, get_models_request
        #)
        self.__log.warn("get_models: executed")
        return response

    @inject
    async def get_model(
        self, get_model_request: "GetModelRequest",
        model_manager: ModelManager=Provide[Application.managers.model_manager]
    ) -> "GetModelResponse":
        with MeasureDuration() as m:
            response = model_manager.get_model(get_model_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, model_manager.get_model, get_model_request
        #)
        self.__log.warn("get_model: executed")
        return response

    @inject
    async def delete_model(
        self, delete_model_request: "DeleteModelRequest",
        model_manager: ModelManager=Provide[Application.managers.model_manager]
    ) -> "DeleteModelResponse":
        with MeasureDuration() as m:
            response = model_manager.delete_model(delete_model_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, model_manager.delete_model, delete_model_request
        #)
        self.__log.warn("delete_model: executed")
        return response


    @inject
    async def start_explainer_dashboard(
        self, start_dashboard_request: "StartDashboardRequest",
        model_manager: ModelManager=Provide[Application.managers.model_manager]
    ) -> "StartDashboardResponse":
        with MeasureDuration() as m:
            response = model_manager.start_explainer_dashboard(start_dashboard_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, model_manager.delete_model, delete_model_request
        #)
        self.__log.warn("start_explainer_dashboard: executed")
        return response


    @inject
    async def stop_explainer_dashboard(
        self, stop_dashboard_request: "StopDashboardRequest",
        model_manager: ModelManager=Provide[Application.managers.model_manager]
    ) -> "StopDashboardResponse":
        with MeasureDuration() as m:
            response = model_manager.stop_explainer_dashboard(stop_dashboard_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, model_manager.delete_model, delete_model_request
        #)
        self.__log.warn("start_explainer_dashboard: executed")
        return response



#endregion

    ####################################
    ## ONTOLOGY RELATED OPERATIONS
    ####################################
#region


    @inject
    async def get_auto_ml_solutions_for_configuration(
        self,
        get_auto_ml_solutions_for_configuration_request: "GetAutoMlSolutionsForConfigurationRequest",
        ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager]
    ) -> "GetAutoMlSolutionsForConfigurationResponse":
        with MeasureDuration() as m:
            response = ontology_manager.get_auto_ml_solutions_for_configuration(get_auto_ml_solutions_for_configuration_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, ontology_manager.get_auto_ml_solutions_for_configuration, get_auto_ml_solutions_for_configuration_request
        #)
        self.__log.warn("get_auto_ml_solutions_for_configuration: executed")
        return response

    @inject
    async def get_available_strategies(
        self, get_available_strategies_request: "GetAvailableStrategiesRequest",
        ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager],
        data_storage: DataStorage=Provide[Application.ressources.data_storage]
    ) -> "GetAvailableStrategiesResponse":

        found, dataset = data_storage.get_dataset(get_available_strategies_request.user_id, get_available_strategies_request.dataset_id)

        if not found:
            self.__log.error(f"get_available_strategies: dataset {get_available_strategies_request.dataset_id} for user {get_available_strategies_request.user_id} not found")

        #TODO add to ontology and RdfManager
        with MeasureDuration() as m:
            result = GetAvailableStrategiesResponse()
            result.strategies = []
            if dataset["type"] in [":tabular", ":text", ":time_series"]:
                if (not found) or (len(dataset['analysis']['duplicate_columns']) != 0):
                    result.strategies.append(
						Strategy(
						'preprocessing.ignore_redundant_features',
						'Ignore redundant features',
						'This strategy ignores certain dataset columns if they have been flagged as duplicate in the dataset analysis.'
						)
					)

                if (not found) or (len(dataset['analysis']['duplicate_rows']) != 0):
                    result.strategies.append(
                        Strategy(
						'preprocessing.ignore_redundant_samples',
						'Ignore redundant samples',
						'This strategy ignores certain dataset rows if they have been flagged as duplicate in the dataset analysis.'
						)
					)

                size_time_ratio = dataset['analysis']['size_bytes'] / int(get_available_strategies_request.configuration['runtimeLimit'])

                if (not found) or (size_time_ratio > 20000):
                    result.strategies.append(
						Strategy(
						'preprocessing.split_large_datasets',
						'Split large datasets',
						'This strategy truncates the training data if the time limit is relatively short for the size of the dataset.'
						)
				    )

                if  (not found or size_time_ratio > 20000 ):
                     #or ('irrelevant_features' in dataset['analysis'] and len(dataset['analysis']['irrelevant_features']) != 0))
                   # and 'preprocessing.ignore_redundant_samples' not in create_training_request.selected_strategies

                    result.strategies.append(
                        Strategy(
                            'preprocessing.data_sampling',
                            'Data Sampling',
                            'This strategy adds or removes data samples for a better distribution of the class.'
                        )
                    )

                if (not found) or ('irrelevant_features' in dataset['analysis'] and len(dataset['analysis']['irrelevant_features']) != 0):
                    result.strategies.append(
                        Strategy(
                        'preprocessing.feature_selection',
                        'Feature selection',
                        'This strategy will analyse the dataset for irrelevant dimensionality and reduces it to decrease complexity.'
                        )
                    )

            result.strategies.append(
                Strategy(
                'pre_training.top_3_models',
                'Top 3 Models',
                'This strategy will run all adapters with only a small part of the data. Then it will train the 3 best solutions with the full data again.'
                )
            )

            result.strategies.append(
                Strategy(
                'pre_training.multi_fidelity',
                'Multi Fidelity',
                'This strategy will run all adapters with only a small part of the data. Then it will train the best half solutions with more data again and so on, until one last adapter is trained with the full data.'
                )
            )


            result.strategies.append(
                Strategy(
                'preprocessing.pca_feature_extraction',
                'PCA Feature Extraction',
                '...'
                )
            )

        return result

    @inject
    async def get_dataset_types(
        self, get_dataset_types_request: "GetDatasetTypesRequest",
        ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager]
    ) -> "GetDatasetTypesResponse":
        with MeasureDuration() as m:
            response = ontology_manager.get_dataset_types()
        #response = await self.__loop.run_in_executor(
        #    self.__executor, ontology_manager.get_dataset_types
        #)
        self.__log.warn("get_dataset_types: executed")
        return response

    @inject
    async def get_ml_libraries_for_task(
        self, get_ml_libraries_for_task_request: "GetMlLibrariesForTaskRequest",
        ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager]
    ) -> "GetMlLibrariesForTaskResponse":
        with MeasureDuration() as m:
            response = ontology_manager.get_ml_libraries_for_task(get_ml_libraries_for_task_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, ontology_manager.get_ml_libraries_for_task, get_ml_libraries_for_task_request
        #)
        self.__log.warn("get_ml_libraries_for_task: executed")
        return response

    @inject
    async def get_objects_information(
        self, get_objects_information_request: "GetObjectsInformationRequest",
        ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager]
    ) -> "GetObjectsInformationResponse":
        with MeasureDuration() as m:
            response = ontology_manager.get_objects_information(get_objects_information_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, ontology_manager.get_objects_information, get_objects_information_request
        #)
        self.__log.warn("get_objects_information: executed")
        return response

    @inject
    async def get_tasks_for_dataset_type(
        self, get_tasks_for_dataset_type_request: "GetTasksForDatasetTypeRequest",
        ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager]
    ) -> "GetTasksForDatasetTypeResponse":
        with MeasureDuration() as m:
            response = ontology_manager.get_tasks_for_dataset_type(get_tasks_for_dataset_type_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, ontology_manager.get_tasks_for_dataset_type, get_tasks_for_dataset_type_request
        #)
        self.__log.warn("get_tasks_for_dataset_type: executed")
        return response

    @inject
    async def get_auto_ml_parameters(
        self, get_auto_ml_parameters_request: GetAutoMlParametersRequest,
        ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager]
    ) -> GetAutoMlParametersResponse:
        with MeasureDuration() as m:
            response = ontology_manager.get_auto_ml_parameters(get_auto_ml_parameters_request)
        #response = await self.__loop.run_in_executor(
        #    self.__executor, ontology_manager.get_tasks_for_dataset_type, get_tasks_for_dataset_type_request
        #)
        self.__log.warn("get_auto_ml_parameters: executed")
        return response

#endregion

    ####################################
    ## PREDICTION DATASET RELATED OPERATIONS
    ####################################
#region


    @inject
    async def create_prediction(
        self, create_prediction_request: "CreatePredictionRequest",
        predictionManager: PredictionManager=Provide[Application.managers.prediction_manager]
    ) -> "CreatePredictionResponse":
        with MeasureDuration() as m:
            response = predictionManager.create_prediction(create_prediction_request)
        self.__log.warn("create_prediction: executed")
        return response

    @inject
    async def get_predictions(
        self, get_predictions_request: "GetPredictionsRequest",
        predictionManager: PredictionManager=Provide[Application.managers.prediction_manager]
    ) -> "GetPredictionsResponse":
        with MeasureDuration() as m:
            response = predictionManager.get_predictions(get_predictions_request)
        self.__log.warn("get_predictions: executed")
        return response

    @inject
    async def get_prediction(
        self, get_prediction_request: "GetPredictionRequest",
        predictionManager: PredictionManager=Provide[Application.managers.prediction_manager]
    ) -> "GetPredictionResponse":
        with MeasureDuration() as m:
            response = predictionManager.get_prediction(get_prediction_request)
        self.__log.warn("get_prediction: executed")
        return response

    @inject
    async def delete_prediction(
        self, delete_prediction_request: "DeletePredictionRequest",
        predictionManager: PredictionManager=Provide[Application.managers.prediction_manager]
    ) -> "DeletePredictionResponse":
        with MeasureDuration() as m:
            response = predictionManager.delete_prediction(delete_prediction_request)
        self.__log.warn("delete_prediction: executed")
        return response

#endregion
