from IAutoMLManager import IAutoMLManager
import Controller_pb2
import Controller_pb2_grpc

class AutoMLSession(object):
    """
    Implementation of an AutoML session object
    """
    def __init__(self, id: int, task: int):
        """
        Init a new instance of AutoMLSession
        ---
        Parameter
        1. id: session id as an int
        2. task: ML task as an int
        """
        self.__id = id
        self.__task = task
        self.__automls = []

    def AddAutoMLToSession(self, automl: IAutoMLManager):
        """
        Add an AutoML to the current session
        ---
        Parameter
        1. automl the automl object implementing the IAutoMLManager
        """
        self.__automls.append(automl)
        return

    def GetId(self) -> str:
        """
        Get the session id
        ---
        Return session id as str
        """
        return str(self.__id)

    def GetAutoMlModel(self, request) -> Controller_pb2.GetAutoMlModelResponse:
        """
        Get the AutoML model of requested AutoML
        ---
        Parameter
        1. request: info about what AutoML the model is to be retrieved
        ---
        Return AutoML model as Controller_pb2.GetAutoMlModelResponse
        """
        for automl in self.__automls:
            if automl.name == request.autoMl:
                return automl.GetAutoMlModel()

    def GetSessionStatus(self) -> Controller_pb2.GetSessionStatusResponse:
        """
        Get the session status
        ---
        Return the session status as Controller_pb2.GetSessionStatusResponse
        """
        response = Controller_pb2.GetSessionStatusResponse()
        response.status = Controller_pb2.SESSION_STATUS_COMPLETED
        for automl in self.__automls:
            response.automls.append(automl.GetStatus())
            if automl.IsRunning() == True:
                response.status = Controller_pb2.SESSION_STATUS_BUSY
        return response