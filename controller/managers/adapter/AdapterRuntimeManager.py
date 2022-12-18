
from enum import auto
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from DataAnalysisAgent import DataAnalysisAgent
from DataStorage import DataStorage
import logging, os
from ControllerBGRPC import *
from AdapterManager import AdapterManager
import Blackboard
import StrategyController
from ExplainableAIManager import ExplainableAIManager
from ThreadLock import ThreadLock


class AdapterRuntimeManager:
    """The AdapterRuntimeManager represent a single training session started by a user and manages it
    """

    def __init__(self, data_storage: DataStorage, request: CreateTrainingRequest, training_id: str, dataset, explainable_lock: ThreadLock) -> None:
        """Initialize a new AdapterRuntimeManager instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            request (CreateTrainingRequest): The GRPC request message holding the training configuration
            training_id (str): The training id which identify the new training session
            dataset (_type_): The dataset record used by the training session
            explainable_lock (ThreadLock): The explainable lock instance to protect from multiple thread using critical parts of the ExplainableAIManager module
        """
        self.__data_storage: DataStorage = data_storage
        self.__request: CreateTrainingRequest = request
        self.__training_id = training_id
        self.__dataset = dataset
        self.__explainable_lock = explainable_lock
        self.__log = logging.getLogger('AdapterRuntimeManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__automl_addresses = {
            ":autokeras":       ["AUTOKERAS_SERVICE_HOST", "AUTOKERAS_SERVICE_PORT"],
            ":flaml":           ["FLAML_SERVICE_HOST",     "FLAML_SERVICE_PORT"],
            ":autosklearn":     ["SKLEARN_SERVICE_HOST",   "SKLEARN_SERVICE_PORT"],
            ":autogluon":       ["AUTOGLUON_SERVICE_HOST", "AUTOGLUON_SERVICE_PORT"],
            ":autocve":         ["AUTOCVE_SERVICE_HOST",   "AUTOCVE_SERVICE_PORT"],
            ":autopytorch":     ["PYTORCH_SERVICE_HOST",   "PYTORCH_SERVICE_PORT"],
            ":mljar":           ["MLJAR_SERVICE_HOST",     "MLJAR_SERVICE_PORT"],
            ":alphad3m":        ["ALPHAD3M_SERVICE_HOST",  "ALPHAD3M_SERVICE_PORT"],
            ":mcfly":           ["MCFLY_SERVICE_HOST", "MCFLY_SERVICE_PORT"],
        }
        self.__adapters: list[AdapterManager] = []
        self.__blackboard = Blackboard.Blackboard()
        self.__strategy_controller = StrategyController.StrategyController(self.__blackboard, self, self.__data_storage)
        AdapterRuntimeManagerAgent(self.__blackboard, self.__strategy_controller, self)
        DataAnalysisAgent(self.__blackboard, self.__strategy_controller, self.__dataset)
        return

    def __adapter_finished_callback(self, training_id, user_id, model_id, model_details: 'dict[str, object]', adapter_manager: AdapterManager):
        """persists the AutoML adapter training session results

        Args:
            training_id (_type_): The training id which identify the new training session
            user_id (_type_): Unique user id saved within the MS Sql database of the frontend
            model_id (_type_): Unique model record id that will be updated
            model_details (dict[str, object]): The dictonary of fields that will be updated inside the model record
            adapter_manager (AdapterManager): The calling AdapterManager, passed to the ExplanableAIManager to connect to the same adapter to start the explanation process
        """
        # lock data storage to prevent race condition between get and update
        import datetime
        with self.__data_storage.lock():
            # append new model to training
            found, training = self.__data_storage.get_training(user_id, training_id)
            found, dataset = self.__data_storage.get_dataset(user_id, training["dataset_id"])
            _mdl_id = self.__data_storage.update_model(user_id, model_id, model_details)
            model_list = self.__data_storage.get_models(user_id, training_id)
            if len(training["model_ids"]) == len(model_list)-1:
                training_details = {
                    "model_ids": training["model_ids"] + [model_id],
                    "status": "ended",
                    "runtime_profile": training["runtime_profile"]
                }
                training_details["runtime_profile"]["end_time"] = datetime.datetime.now()
                self.__data_storage.update_training(user_id, training_id, training_details)
            else:
                self.__data_storage.update_training(user_id, training_id, {
                    "model_ids": training["model_ids"] + [model_id]
                })

        if model_details["status"] == "completed":
            if dataset["type"] in  [":tabular", ":text", ":time_series"]:
                ExplainableAIManager(self.__data_storage, adapter_manager, self.__explainable_lock).explain(user_id, model_id)
                return

    def get_training_id(self) -> str:
        """Get the training id to which the found model is linked too

        Returns:
            str: The training id
        """
        return self.__training_id

    def get_user_id(self) -> str:
        """Get the user id to which the found model is linked too

        Returns:
            str: The user id
        """
        return self.__request.user_id

    def get_status_for_blackboard(self) -> dict:
        """Get the current general training status for the blackboard

        Returns:
            dict: The current general training status
        """
        status = "completed"
        for automl in self.__adapters:
            if automl.is_running():
                status = "busy"
        return {
            'training_id': self.__training_id,
            'status': status,
            'configuration': self.__request.to_dict(),
        }

    def get_training_request(self) -> "CreateTrainingRequest":
        """Get the training request object

        Returns:
            CreateTrainingRequest: The training request object
        """
        return self.__request

    def get_dataset(self):
        """Get the dataset record used by the training

        Returns:
            _type_: The dataset record
        """
        return self.__dataset

    def create_new_training(self):
        """Initialize the required AdapterManager for this training session and kick off strategy controller timer to begin training process
        """
        self.__log.debug("start_new_training: creating new blackboard and strategy controller for training")
        for automl in self.__request.configuration.selected_auto_ml_solutions:
            self.__log.debug(f"start_new_training: getting adapter endpoint information for automl {automl}")
            host, port = map(os.getenv, self.__automl_addresses[automl.lower()])
            port = int(port)
            self.__log.debug(f"start_new_training: creating new adapter manager and adapter manager agent")
            adapter_training = AdapterManager(self.__data_storage, self.__request, automl, self.__training_id, self.__dataset, host, port, self.__blackboard, self.__strategy_controller, self.__adapter_finished_callback)
            self.__adapters.append(adapter_training)

        self.__strategy_controller.on_event('phase_updated', self.blackboard_phase_update_handler)
        self.__strategy_controller.set_phase('preprocessing')
        self.__strategy_controller.start_timer()

    def blackboard_phase_update_handler(self, meta, controller):
        """Handles phase updates throughout the session (caused by the strategy controller)

        Args:
            meta (_type_): The event meta (contains a dict holding the "old_phase" and "new_phase")
            controller (_type_): The strategy controller instance that caused the event
        """
        if meta.get('old_phase') == 'preprocessing' and meta.get('new_phase') == 'running':
            # Preprocessing finished, start the AutoML training
            self.__phase_start_automl_training()

    def __phase_start_automl_training(self):
        """Start the AutoML adapter training process by starting the AdapterManager task
        """
        for automl in self.__adapters:
            self.__log.debug(f"__phase_start_automl_training: adapter endpoint information for automl {automl}")
            automl.start()
