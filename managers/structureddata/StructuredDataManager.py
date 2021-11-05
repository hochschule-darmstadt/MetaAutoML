from AutoKerasManager import AutoKerasManager
from FLAMLManager import FLAMLManager
from MljarManager import MljarManager
from AutoMLSession import AutoMLSession

class StructuredDataManager(object):
    """
    Implementation of a Structured data manager responsible for executing structured data AutoML sessions
    """

    def __init__(self):
        """
        Init a new instance of the StructuredDataManager
        """
        return

    def StartAutoML(self, configuration, folder_location, sessionId) -> AutoMLSession:
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
        #FUTURE ADD CONDITION TO ONLY START REQUIRED AUTOML
        autoKeras = AutoKerasManager(configuration, folder_location)
        flaml = FLAMLManager(configuration, folder_location)
        #mljar = MljarManager(configuration, folder_location)
        newSession = AutoMLSession(sessionId, configuration.task)
        autoKeras.start()
        flaml.start()
        #mljar.start()
        newSession.AddAutoMLToSession(autoKeras)
        newSession.AddAutoMLToSession(flaml)
        #newSession.AddAutoMLToSession(mljar)
        return newSession
