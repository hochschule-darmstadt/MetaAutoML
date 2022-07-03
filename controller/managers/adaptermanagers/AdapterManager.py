from AutoMLSession import AutoMLSession
from Controller_bgrpc import *
from AutoMLManager import AutoMLManager
import os


class AdapterManager(object):
    """
    Implementation of a Structured data manager responsible for executing structured data AutoML sessions
    """

    def start_automl(self, configuration: "StartAutoMlProcessRequest", folder_location, session_id, callback) -> AutoMLSession:
        """
        Start a new AutoML session
        ---
        Parameter
        1. configuration dictionary
        2. folder location of the dataset
        3. session id to use
        ---
        Return a new AutoMLSession object
        """
        # map all automl names with their host names and port names
        automl_addresses = {
            "autokeras":   ["AUTOKERAS_SERVICE_HOST", "AUTOKERAS_SERVICE_PORT"],
            "flaml":        ["FLAML_SERVICE_HOST",     "FLAML_SERVICE_PORT"],
            "autosklearn":  ["SKLEARN_SERVICE_HOST",   "SKLEARN_SERVICE_PORT"],
            "autogluon":    ["AUTOGLUON_SERVICE_HOST", "AUTOGLUON_SERVICE_PORT"],
            "autocve":      ["AUTOCVE_SERVICE_HOST",   "AUTOCVE_SERVICE_PORT"],
            "autopytorch": ["PYTORCH_SERVICE_HOST",   "PYTORCH_SERVICE_PORT"],
            "mljar":        ["MLJAR_SERVICE_HOST",     "MLJAR_SERVICE_PORT"],
        }

        automl_names: list[str] = configuration.required_auto_mls
        if not configuration.required_auto_mls:
            print('No AutoMLs specified in the request. Running all available AutoMLs.')
            automl_names = list(automl_addresses.keys())

        # collect all AutoMLManager instances
        automls: list[AutoMLManager] = []
        for automl_name in automl_names:
            # get host and port from environment variables
            host, port = map(os.getenv, automl_addresses[automl_name.lower()])
            port = int(port)

            automl = AutoMLManager(configuration, folder_location, host, port, session_id, callback)
            # NOTE: friendly name for the thread, also relevant for the callback
            automl.name = automl_name

            automls.append(automl)

        # start session and all AutoMLManager threads
        new_session = AutoMLSession(session_id, configuration)
        for automl in automls:
            automl.start()
            new_session.add_automl_to_session(automl)
        return new_session
