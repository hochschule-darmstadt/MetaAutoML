import threading
from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import json, logging, os
from RdfManager import RdfManager
from CsvManager import CsvManager
from LongitudinalDataManager import LongitudinalDataManager

class TrainingManager:

    def __init__(self, storage_dir: str, mongo_db_url: str, storage_lock: threading.Lock) -> None:
        self.__data_storage: DataStorage = DataStorage(storage_dir, storage_lock, mongo_db_url)
        self.__log = logging.getLogger('TrainingManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        

    def create_training(
        self, create_training_request: "CreateTrainingRequest"
    ) -> "CreateTrainingResponse":
        """
        Create a new training run
        ---
        Parameter
        1. training information
        ---
        Return empty CreateTrainingResponse object
        """
        response = CreateTrainingResponse()
        
        self.__log.debug(f"create_training: trying to get dataset {create_training_request.dataset_identifier} for user {create_training_request.user_identifier}")
        found, dataset = self.__data_storage.get_dataset(create_training_request.user_identifier, create_training_request.dataset_identifier)
        if not found:
            self.__log.error(f"create_training: dataset {create_training_request.dataset_identifier} for user {create_training_request.user_identifier} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Training {create_training_request.dataset_identifier} for user {create_training_request.user_identifier} not found, already deleted?")
        
        # TODO: rework file access in AutoMLSession
        #       we do not want to make datastore paths public
        dataset_folder = os.path.dirname(dataset["path"])
        dataset_filename = os.path.basename(dataset["path"])

        # overwrite dataset name for further processing
        #   frontend sends dataset name ("titanic_train_1.csv"), 
        #   but datasets on disk are saved as dataset_id ("629e323a9290ff0cf5a5d4a9")
       # create_training_request.dataset = dataset_filename
        
        self.__log.debug(f"create_training: generating training details")
        config = {
            "dataset_id": str(dataset["_id"]),
            "dataset_name": dataset["name"],
            "task": create_training_request.task,
            "configuration": json.loads(create_training_request.configuration),
            "dataset_configuration": json.loads(create_training_request.dataset_configuration),
            "runtime_constraints": json.loads(create_training_request.runtime_constraints),
            "test_configuration": json.loads(create_training_request.test_configuration),
            "metric": create_training_request.metric,
            "status": "busy",
            "models": [],
            "selected_automls": list(create_training_request.selected_auto_mls),
            "selected_libraries": list(create_training_request.selected_libraries),
            "start_time": datetime.now()
        }
        
        training_id = self.__data_storage.create_training(create_training_request.user_identifier, config)
        self.__log.debug(f"create_training: inserted new training: {training_id}")

        # TODO REWORK AUTOML SESSION PROCESS
        # will be called when any automl is done
        # NOTE: will run in parallel
        def callback(training_id, model_id, model: 'dict[str, object]'):
            # lock data storage to prevent race condition between get and update
            self.__data_storage.lock()
            # append new model to training
            training = self.__data_storage.get_training(create_training_request.user_identifier, training_id)
            found, dataset = self.__data_storage.get_dataset(create_training_request.user_identifier, training["dataset_id"])
            model["dataset_id"] = training["dataset_id"]
            _mdl_id = self.__data_storage.update_model(create_training_request.user_identifier, model_id, model)
            model_list = self.__data_storage.get_models(create_training_request.user_identifier, training_id)
            if len(training["models"]) == len(model_list)-1:
                self.__data_storage.update_training(create_training_request.user_identifier, training_id, {
                    "models": training["models"] + [model_id],
                    "status": "completed",
                    "dataset_configuration": json.loads(create_training_request.dataset_configuration),
                    "end_time": datetime.now()
                })
            else:
                self.__data_storage.update_training(create_training_request.user_identifier, training_id, {
                    "models": training["models"] + [model_id],
                    "dataset_configuration": json.loads(create_training_request.dataset_configuration)
                })
            self.__data_storage.unlock()

            if model["status"] == "completed":
                if dataset["type"] == ":tabular" or dataset["type"] == ":text" or dataset["type"] == ":time_series":
                    self.__explainableAIManager.explain(create_training_request.user_identifier, model_id)

        #newTraining: AutoMLSession = self.__adapterManager.start_automl(create_training_request,
        #                                                                str(dataset["_id"]),
        #                                                                dataset_folder,
        #                                                                training_id,
        #                                                                create_training_request.user_identifier,
         #                                                               callback)

        #self.__trainings[training_id] = newTraining
        #response.result = 1
        #response.training_identifier = newTraining.get_id()
        return response

    def get_trainings(
        self, get_trainings_request: "GetTrainingsRequest"
    ) -> "GetTrainingsResponse":
        """
        Get all trainings for a specific user
        ---
        Parameter
        1. grpc request object, containing the user identifier
        ---
        Return a list of compatible trainings or a GRPC error UNAVAILABLE for read errors
        """
        response = GetTrainingsResponse() 
        self.__log.debug(f"get_trainings: get all trainings for user {get_trainings_request.user_identifier}")
        all_trainings: list[dict[str, object]] = self.__data_storage.get_trainings(get_trainings_request.user_identifier)
        self.__log.debug(f"get_trainings: found {all_trainings.count} trainings for user {get_trainings_request.user_identifier}")
        
        for training in all_trainings:
            try:
                trainingItem = Training()

                self.__log.debug("get_trainings: get all models for training")
                training_models = self.__data_storage.get_models(get_trainings_request.user_identifier, str(training["_id"]))
                self.__log.debug(f"get_trainings: found {training_models.count} models")
        
                trainingItem.status = training["status"]

                for model in list(training_models):
                    try:
                        adapterStatus = AdapterStatus()
                        adapterStatus.identifier = str(model["_id"])
                        adapterStatus.name = model["automl_name"]
                        adapterStatus.status = model["status"]
                        adapterStatus.messages[:] =  model["status_messages"]
                        adapterStatus.test_score =  model["test_score"]
                        adapterStatus.validation_score =  model["validation_score"]
                        adapterStatus.runtime =  model["runtime"]
                        adapterStatus.predictiontime =  model["prediction_time"]
                        adapterStatus.model =  model["model"]
                        adapterStatus.library =  model["library"]
                        trainingItem.adapters.append(adapterStatus)
                        trainingItem.identifier = str(model["_id"])
                        trainingItem.dataset_identifier = model["dataset_id"]
                    except Exception as e:
                        self.__log.error(f"get_trainings: Error while reading parameter for model")
                        self.__log.error(f"get_trainings: exception: {e}")
                        raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model")

                trainingItem.dataset_identifier = training["dataset_id"]
                trainingItem.dataset_name = training["dataset_name"]
                trainingItem.task = training["task"]
                trainingItem.configuration = json.dumps(training["configuration"])
                trainingItem.start_time = training["start_time"]
                trainingItem.identifier = str(training["_id"])
                for automl in training['required_automls']:
                    trainingItem.selected_auto_mls.append(automl)
                for lib in training['required_libraries']:
                    trainingItem.selected_ml_libraries.append(lib)
                trainingItem.runtime_constraints = json.dumps(training["runtime_constraints"])
                trainingItem.dataset_configuration = json.dumps(training["dataset_configuration"])
            
                trainingItem.events = []
                for event in training.get('events', []):
                    response_event = StrategyControllerEvent()
                    response_event.type = event.get('type')
                    response_event.meta = json.dumps(event.get('meta'))
                    response_event.timestamp = event.get('timestamp')
                    trainingItem.events.append(response_event)

                response.trainings.append(trainingItem)
            except Exception as e:
                    self.__log.error(f"get_trainings: Error while reading parameter for training")
                    self.__log.error(f"get_trainings: exception: {e}")
                    raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Training")

        return response

    def get_training(
        self, get_training_request: "GetTrainingRequest"
    ) -> "GetTrainingResponse":
        """
        Get training details for a specific dataset
        ---
        Parameter
        1. grpc request object, containing the user, and traininig identifier
        ---
        Return dataset details
        The result is a GetTrainingResponse object describing one dataset or a GRPC error if ressource NOT_FOUND or UNAVAILABLE for read errors
        """
        response = GetTrainingResponse() 
        found, training = self.__data_storage.get_training(get_training_request.user_identifier, get_training_request.training_identifier)
        if not found:
            self.__log.error(f"get_training: training {get_training_request.training_identifier} for user {get_training_request.user_identifier} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Training {get_training_request.training_identifier} for user {get_training_request.user_identifier} not found, already deleted?")
        try:
            self.__log.debug("get_training: get all models for training")
            training_models = self.__data_storage.get_models(get_training_request.user_identifier, get_training_request.training_identifier)
            self.__log.debug(f"get_training: found {training_models.count} models")
            for model in list(training_models):
                try:
                    adapterStatus = AdapterStatus()
                    adapterStatus.identifier = str(model["_id"])
                    adapterStatus.name = model["automl_name"]
                    adapterStatus.status = model["status"]
                    adapterStatus.messages[:] =  model["status_messages"]
                    adapterStatus.test_score =  model["test_score"]
                    adapterStatus.validation_score =  model["validation_score"]
                    adapterStatus.runtime =  model["runtime"]
                    adapterStatus.predictiontime =  model["prediction_time"]
                    adapterStatus.model =  model["model"]
                    adapterStatus.library =  model["library"]
                    response.training.adapters.append(adapterStatus)
                except Exception as e:
                    self.__log.error(f"get_training: Error while reading parameter for model")
                    self.__log.error(f"get_training: exception: {e}")
                    raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model")
                        
            response.training.status = training["status"]
            response.training.dataset_identifier = training["dataset_id"]
            response.training.dataset_name = training["dataset_name"]
            response.training.task = training["task"]
            response.training.start_time = training["start_time"]
            response.training.identifier = str(training["_id"])
            response.training.configuration = json.dumps(training["configuration"])
            for automl in training['required_automls']:
                response.training.selected_auto_mls.append(automl)
            for lib in training['required_libraries']:
                response.training.selected_ml_libraries.append(lib)
            response.training.runtime_constraints = json.dumps(training["runtime_constraints"])
            response.training.dataset_configuration = json.dumps(training["dataset_configuration"])
                
            response.training.events = []
            for event in training.get('events', []):
                response_event = StrategyControllerEvent()
                response_event.type = event.get('type')
                response_event.meta = json.dumps(event.get('meta'))
                response_event.timestamp = event.get('timestamp')
                response.training.events.append(response_event)
        except Exception as e:
            self.__log.error(f"get_training: Error while reading parameter for training {get_training_request.training_identifier} for user {get_training_request.user_identifier}")
            self.__log.error(f"get_training: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Training {get_training_request.training_identifier} for user {get_training_request.user_identifier}")


        return response

    def delete_training(
        self, delete_training_request: "DeleteTrainingRequest"
    ) -> "DeleteTrainingResponse":
        """
        Delete a training from database and disc
        ---
        Parameter
        1. grpc request object containing the user, training identifier
        ---
        Return empty DeleteTrainingResponse object or a GRPC error if ressource NOT_FOUND
        """
        self.__log.debug(f"delete_training: deleting training {delete_training_request.training_identifier}, of user {delete_training_request.user_identifier}")
        result = self.__data_storage.delete_dataset(delete_training_request.user_identifier, delete_training_request.training_identifier)
        self.__log.debug(f"delete_training: {str(result)} trainings deleted")
        return DeleteTrainingResponse()