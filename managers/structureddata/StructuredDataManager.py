from AutoKerasManager import AutoKerasManager
from FLAMLManager import FLAMLManager
from MljarManager import MljarManager
from AutoMLSession import AutoMLSession
from SklearnManager import SklearnManager
from AutoCVEManager import AutoCVEManager


class StructuredDataManager(object):
    """
    Implementation of a Structured data manager responsible for executing structured data AutoML sessions
    """

    def __init__(self):
        """
        Init a new instance of the StructuredDataManager
        """
        return

    def start_automl(self, configuration, folder_location, session_id) -> AutoMLSession:
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
        # FUTURE ADD CONDITION TO ONLY START REQUIRED AUTOML
        auto_keras = AutoKerasManager(configuration, folder_location)
        flaml = FLAMLManager(configuration, folder_location)
        auto_sklearn = SklearnManager(configuration, folder_location)
        auto_cve = AutoCVEManager(configuration, folder_location)
        # mljar = MljarManager(configuration, folder_location)

        new_session = AutoMLSession(session_id, configuration.task)
        auto_keras.start()
        flaml.start()
        auto_sklearn.start()
        auto_cve.start()
        # mljar.start()

        new_session.AddAutoMLToSession(auto_keras)
        new_session.AddAutoMLToSession(flaml)
        new_session.AddAutoMLToSession(auto_sklearn)
        new_session.AddAutoMLToSession(auto_cve)
        # new_session.AddAutoMLToSession(mljar)

        return new_session
