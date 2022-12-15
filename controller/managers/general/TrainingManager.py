from subprocess import call
import threading
from DataStorage import DataStorage
from ControllerBGRPC import *
import json, logging, os, datetime
from AdapterRuntimeScheduler import AdapterRuntimeScheduler

class TrainingManager:
    """The TrainingManager provides all functionality related to Trainings objects
    """

    def __init__(self, data_storage: DataStorage, adapter_runtime_scheduler: AdapterRuntimeScheduler) -> None:
        """Initialize a new TrainingManager instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            adapter_runtime_scheduler (AdapterRuntimeScheduler): The AdapterRuntimeScheduler managing the training processes within the controller
        """
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('TrainingManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__adapter_runtime_scheduler = adapter_runtime_scheduler

    async def create_training(
        self, create_training_request: "CreateTrainingRequest"
    ) -> "CreateTrainingResponse":
        """Create a new training record and start the training process

        Args:
            create_training_request (CreateTrainingRequest): GRPC message holding the user id and training configuration for the new training

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if no dataset record was found
            grpclib.GRPCError: grpclib.Status.CANCELLED, raised if the AutoML list field inside the config is empty
            grpclib.GRPCError: grpclib.Status.CANCELLED, raised if the ML Library list field inside the config is empty

        Returns:
            CreateTrainingResponse: The GRPC response message holding the newly created training record id
        """
        response = CreateTrainingResponse()
        
        self.__log.debug(f"create_training: trying to get dataset {create_training_request.dataset_id} for user {create_training_request.user_id}")
        found, dataset = self.__data_storage.get_dataset(create_training_request.user_id, create_training_request.dataset_id)
        if not found:
            self.__log.error(f"create_training: dataset {create_training_request.dataset_id} for user {create_training_request.user_id} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Training {create_training_request.dataset_id} for user {create_training_request.user_id} not found, already deleted?")
        
        if not create_training_request.configuration.selected_auto_ml_solutions:
            self.__log.error(f"create_training: user {create_training_request.user_id} started a new run with empty AutoML list.")
            raise grpclib.GRPCError(grpclib.Status.CANCELLED, "started a new run with empty AutoML list, wizard error?")
        
        if not create_training_request.configuration.selected_ml_libraries:
            self.__log.error(f"create_training: user {create_training_request.user_id} started a new run with empty ML library list.")
            raise grpclib.GRPCError(grpclib.Status.CANCELLED, "started a new run with empty ML library list, wizard error?")
        

        # TODO: rework file access in AutoMLSession
        #       we do not want to make datastore paths public
        dataset_folder = os.path.dirname(dataset["path"])
        dataset_filename = os.path.basename(dataset["path"])

        # overwrite dataset name for further processing
        #   frontend sends dataset name ("titanic_train_1.csv"), 
        #   but datasets on disk are saved as dataset_id ("629e323a9290ff0cf5a5d4a9")
       # create_training_request.dataset = dataset_filename
        response.training_id = self.__adapter_runtime_scheduler.create_new_training(create_training_request)
        return response

    def __training_object_rpc_object(self, user_id: str, training: dict) -> Training:
        """Convert a training record dictionary into the GRPC Training object

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            training (dict): The retrieved training record dictionary

        Raises:
            grpclib.GRPCError: grpclib.Status.UNAVAILABLE, raised when a dictionary field could not be read
            grpclib.GRPCError: grpclib.Status.UNAVAILABLE, raised when a dictionary field could not be read

        Returns:
            Training: The GRPC training object generated from the dictonary
        """
        try:
            training_item = Training()

            self.__log.debug("__training_object_rpc_object: get all models for training")
            training_models = self.__data_storage.get_models(user_id, str(training["_id"]))
            self.__log.debug(f"__training_object_rpc_object: found {training_models.count} models")
    
            training_item.id = str(training["_id"])
            training_item.dataset_id = training["dataset_id"]
            for model in training_models:
                try:
                    model_detail = Model()
                    model_detail.id = str(model["_id"])
                    model_detail.training_id = model["training_id"]

                    model_detail.status = model["status"]
                    model_detail.auto_ml_solution = model["auto_ml_solution"]
                    model_detail.ml_model_type =  model["ml_model_type"]
                    model_detail.ml_library =  model["ml_library"]
                    model_detail.path = model["path"]
                    model_detail.test_score =  model["test_score"]
                    model_detail.prediction_time =  model["prediction_time"]

                    model_runtime = ModelruntimeProfile()
                    model_runtime.start_time = model["runtime_profile"]["start_time"]
                    model_runtime.end_time = model["runtime_profile"]["end_time"]
                    model_detail.runtime_profile = model_runtime
                    model_detail.status_messages[:] =  model["status_messages"]
                    model_detail.explanation = json.dumps(model["explanation"])
                    training_item.models.append(model_detail)
                except Exception as e:
                    self.__log.error(f"__training_object_rpc_object: Error while reading parameter for model")
                    self.__log.error(f"__training_object_rpc_object: exception: {e}")
                    raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model")

            training_item.status = training["status"]

            training_configuration = Configuration()
            training_configuration.task = training["configuration"]["task"]
            training_configuration.target = training["configuration"]["target"]
            training_configuration.enabled_strategies = training["configuration"]["enabled_strategies"]
            training_configuration.runtime_limit = training["configuration"]["runtime_limit"]
            training_configuration.metric = training["configuration"]["metric"]
            training_configuration.selected_auto_ml_solutions = training["configuration"]["selected_auto_ml_solutions"]
            training_configuration.selected_ml_libraries = training["configuration"]["selected_ml_libraries"]
            training_item.configuration = training_configuration

            training_item.dataset_configuration = json.dumps(training["dataset_configuration"])

            training_runtime_profile = TrainingRuntimeProfile()
            training_runtime_profile.start_time = training["runtime_profile"]["start_time"]
            for event in training["runtime_profile"]['events']:
                response_event = StrategyControllerEvent()
                response_event.type = event['type']
                response_event.meta = json.dumps(event['meta'])
                response_event.timestamp = event['timestamp']
                training_runtime_profile.events.append(response_event)

            training_runtime_profile.end_time = training["runtime_profile"]["end_time"]
            training_item.runtime_profile = training_runtime_profile
                
            return training_item
        except Exception as e:
            self.__log.error(f"__training_object_rpc_object: Error while reading parameter for training")
            self.__log.error(f"__training_object_rpc_object: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Training")


    def get_trainings(
        self, get_trainings_request: "GetTrainingsRequest"
    ) -> "GetTrainingsResponse":
        """Get all trainings or get all trainings using an optional filter

        Args:
            get_trainings_request (GetTrainingsRequest): The GRPC request holding the user id and filters

        Returns:
            GetTrainingsResponse: The GRPC response holding the list of found trainings
        """
        response = GetTrainingsResponse() 
        self.__log.debug(f"get_trainings: get all trainings for user {get_trainings_request.user_id}")
        all_trainings: list[dict[str, object]] = self.__data_storage.get_trainings(get_trainings_request.user_id)
        self.__log.debug(f"get_trainings: found {all_trainings.count} trainings for user {get_trainings_request.user_id}")
        
        for training in all_trainings:
            response.trainings.append(self.__training_object_rpc_object(get_trainings_request.user_id, training))
        return response

    def get_training(
        self, get_training_request: "GetTrainingRequest"
    ) -> "GetTrainingResponse":
        """Get training details for a specific training

        Args:
            get_training_request (GetTrainingRequest): The GRPC request holding the user id and and training id

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if no training record was found

        Returns:
            GetTrainingResponse: The GRPC response holding the found training
        """
        response = GetTrainingResponse() 
        found, training = self.__data_storage.get_training(get_training_request.user_id, get_training_request.training_id)
        if not found:
            self.__log.error(f"get_training: training {get_training_request.training_id} for user {get_training_request.user_id} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Training {get_training_request.training_id} for user {get_training_request.user_id} not found, already deleted?")
        response.training = self.__training_object_rpc_object(get_training_request.user_id, training)
        return response

    def delete_training(
        self, delete_training_request: "DeleteTrainingRequest"
    ) -> "DeleteTrainingResponse":
        """Delete a training from database and disc

        Args:
            delete_training_request (DeleteTrainingRequest): The GRPC request containing the user id, training id

        Returns:
            DeleteTrainingResponse: The empty GRPC response
        """
        self.__log.debug(f"delete_training: deleting training {delete_training_request.training_id}, of user {delete_training_request.user_id}")
        result = self.__data_storage.delete_training(delete_training_request.user_id, delete_training_request.training_id)
        self.__log.debug(f"delete_training: {str(result)} trainings deleted")
        return DeleteTrainingResponse()
