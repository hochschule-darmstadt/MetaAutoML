from AutoCVEManager import AutoCVEManager
from AutoGluonManager import AutoGluonManager
from AutoKerasManager import AutoKerasManager
from FLAMLManager import FLAMLManager
from MljarManager import MljarManager
from AutoMLSession import AutoMLSession
from SklearnManager import SklearnManager
from AutoPyTorchManager import AutoPyTorchManager


class AdapterManager(object):
    """
    Implementation of a Structured data manager responsible for executing structured data AutoML sessions
    """

    def start_automl(self, configuration, folder_location, session_id, callback) -> AutoMLSession:
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
        if len(list(configuration.requiredAutoMLs)) == 0:
            print('No AutoMLs specified in the request. Running all available AutoMLs.')
            required_automl_names = ('FLAML', 'Auto_Keras', 'Autosklearn', 'AutoGluon', 'AutoCVE', 'Auto_PyTorch', 'MLJAR')
        else:
            required_automl_names = [name for name in configuration.requiredAutoMLs]

        required_automls = []
        for automl_name in required_automl_names:
            if automl_name == AutoKerasManager.name:
                required_automls.append(AutoKerasManager(configuration, folder_location, session_id, callback))
            elif automl_name == FLAMLManager.name:
                required_automls.append(FLAMLManager(configuration, folder_location, session_id, callback))
            elif automl_name == SklearnManager.name:
                required_automls.append(SklearnManager(configuration, folder_location, session_id, callback))
            elif automl_name == AutoGluonManager.name:
                required_automls.append(AutoGluonManager(configuration, folder_location, session_id, callback))
            elif automl_name == AutoCVEManager.name:
                required_automls.append(AutoCVEManager(configuration, folder_location, session_id, callback))
            elif automl_name == AutoPyTorchManager.name:
                required_automls.append(AutoPyTorchManager(configuration, folder_location, session_id, callback))
            elif automl_name == MljarManager.name:
                required_automls.append(MljarManager(configuration, folder_location, session_id, callback))

        new_session = AutoMLSession(session_id, configuration)
        for automl in required_automls:
            automl.start()
            new_session.add_automl_to_session(automl)
        return new_session
