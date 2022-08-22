from AutoMLSession import AutoMLSession
from Controller_bgrpc import *
from AutoMLManager import AutoMLManager
import os


class AdapterManager(object):
    """
    Implementation of a Structured data manager responsible for executing structured data AutoML sessions
    """
    def __init__(self, data_storage):
        """
        Init a new instance of the abstract class AutoMLManager
        ---
        Parameter
        1. data storage manager
        """
        self.__data_storage = data_storage
        # map all automl names with their host names and port names
        self.__automl_addresses = {
            ":autokeras":   ["AUTOKERAS_SERVICE_HOST", "AUTOKERAS_SERVICE_PORT"],
            ":flaml":        ["FLAML_SERVICE_HOST",     "FLAML_SERVICE_PORT"],
            ":autosklearn":  ["SKLEARN_SERVICE_HOST",   "SKLEARN_SERVICE_PORT"],
            ":autogluon":    ["AUTOGLUON_SERVICE_HOST", "AUTOGLUON_SERVICE_PORT"],
            ":autocve":      ["AUTOCVE_SERVICE_HOST",   "AUTOCVE_SERVICE_PORT"],
            ":autopytorch": ["PYTORCH_SERVICE_HOST",   "PYTORCH_SERVICE_PORT"],
            ":mljar":        ["MLJAR_SERVICE_HOST",     "MLJAR_SERVICE_PORT"],
            ":alphad3m":        ["ALPHAD3M_SERVICE_HOST",  "ALPHAD3M_SERVICE_PORT"],
        }

    def TestAutoml(self, request: TestAutoMlRequest, automl: str, training_id, config):
        host, port = map(os.getenv, self.__automl_addresses[automl.lower()])
        automlInstance =AutoMLManager(config, None, None, host, port, request, training_id, request.username, None)
        return automlInstance.testSolution(request.test_data, training_id, request.username)

    def start_automl(self, configuration: "StartAutoMlProcessRequest", dataset_id, folder_location, training_id, username, callback) -> AutoMLSession:
        """
        Start a new AutoML training
        ---
        Parameter
        1. configuration dictionary
        2. folder location of the dataset
        3. training id to use
        ---
        Return a new AutoMLSession object
        """

        automl_names: list[str] = configuration.required_auto_mls
        if not configuration.required_auto_mls:
            print('No AutoMLs specified in the request. Running all available AutoMLs.')
            automl_names = list(self.__automl_addresses.keys())

        # collect all AutoMLManager instances
        automls: list[AutoMLManager] = []
        for automl_name in automl_names:
            # get host and port from environment variables
            host, port = map(os.getenv, self.__automl_addresses[automl_name.lower()])
            port = int(port)

            automl = AutoMLManager(configuration, dataset_id, folder_location, host, port, training_id, username, self.__data_storage, callback)
            # NOTE: friendly name for the thread, also relevant for the callback
            automl.name = automl_name

            automls.append(automl)

        # start training and all AutoMLManager threads
        session = AutoMLSession(training_id, dataset_id, configuration, self.__data_storage)
        for automl in automls:
            session.add_automl_to_training(automl)
        session.controller.WaitForPhase('running')
        for automl in automls:
            automl.start()
        return session
