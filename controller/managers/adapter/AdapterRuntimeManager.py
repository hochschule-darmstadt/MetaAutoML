
from enum import auto
from AdapterManagerAgent import AdapterManagerAgent
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from DataAnalysisAgent import DataAnalysisAgent
from DataStorage import DataStorage
import json, logging, os, asyncio
from ControllerBGRPC import *
from AdapterManager import AdapterManager
import Blackboard
import StrategyController
from ExplainableAIManager import ExplainableAIManager


class AdapterRuntimeManager:

    def __init__(self, data_storage: DataStorage, request: "CreateTrainingRequest", training_id: str, dataset) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__request = request
        self.__training_id = training_id
        self.__dataset = dataset
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
        # lock data storage to prevent race condition between get and update
        with self.__data_storage.lock():
            # append new model to training
            found, training = self.__data_storage.get_training(user_id, training_id)
            found, dataset = self.__data_storage.get_dataset(user_id, training["dataset_id"])
            _mdl_id = self.__data_storage.update_model(user_id, model_id, model_details)
            model_list = self.__data_storage.get_models(user_id, training_id)
            if len(training["models"]) == len(model_list)-1:
                self.__data_storage.update_training(user_id, training_id, {
                    "models": training["models"] + [model_id],
                    "status": "completed",
                    "end_time": datetime.now()
                })
            else:
                self.__data_storage.update_training(user_id, training_id, {
                    "models": training["models"] + [model_id]
                })

        if model_details["status"] == "completed":
            if dataset["type"] == ":tabular" or dataset["type"] == ":text" or dataset["type"] == ":time_series":
                ExplainableAIManager(self.__data_storage, adapter_manager).explain(user_id, model_id)
                return
    
    def get_training_id(self):
        return self.__training_id

    def get_user_id(self):
        return self.__request.user_id

    def get_status_for_blackboard(self):
        status = "completed"
        for automl in self.__adapters:
            if automl.is_running():
                status = "busy"
        return {
            'training_id': self.__training_id,
            'status': status,
            'configuration': self.__request.to_dict(),
        }

    def get_training_request(self):
        return self.__request

    def get_dataset(self):
        return self.__dataset

    def create_new_training(self):
        self.__log.debug("start_new_training: creating new blackboard and strategy controller for training")
        for automl in self.__request.selected_auto_mls:
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
        """
        Handles phase updates throughout the session (caused by the strategy controller)
        ---
        Parameter
        1. The event meta (contains a dict holding the "old_phase" and "new_phase")
        1. The strategy controller instance that caused the event
        """
        if meta.get('old_phase') == 'preprocessing' and meta.get('new_phase') == 'running':
            # Preprocessing finished, start the AutoML training
            self.__phase_start_automl_training()

    def __phase_start_automl_training(self):
        for automl in self.__adapters:
            self.__log.debug(f"__phase_start_automl_training: adapter endpoint information for automl {automl}")
            automl.start()