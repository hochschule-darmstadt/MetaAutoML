
from Controller_bgrpc import *
from IAutoMLManager import IAutoMLManager
import json

class AutoMLSession(object):
    """
    Implementation of an AutoML session object
    """

    def __init__(self, session_id: int, configuration):
        """
        Init a new instance of AutoMLSession
        ---
        Parameter
        1. id: session id as an int
        2. configuration: session configuration
        """
        self.__id = session_id
        self.__configuration: StartAutoMlProcessRequest = configuration
        self.automls = []

    def add_automl_to_training(self, automl: IAutoMLManager):
        """
        Add an AutoML to the current session
        ---
        Parameter
        1. automl the automl object implementing the IAutoMLManager
        """
        self.automls.append(automl)

    def get_id(self) -> str:
        """
        Get the session id
        ---
        Return session id as str
        """
        return str(self.__id)

    def get_automl_model(self, request: GetAutoMlModelRequest) -> GetAutoMlModelResponse:
        """
        Get the AutoML model of requested AutoML
        ---
        Parameter
        1. request: info about what AutoML the model is to be retrieved
        ---
        Return AutoML model as Controller_pb2.GetAutoMlModelResponse
        """
        for automl in self.automls:
            if automl.name == request.auto_ml:
                return automl.get_automl_model()

    def get_session_status(self) -> GetTrainingResponse:
        """
        Get the session status
        ---
        Return the session status as Controller_pb2.GetSessionStatusResponse
        """

        response = GetTrainingResponse(configuration=self.__configuration.configuration,
                                                            dataset_configuration=self.__configuration.dataset_configuration,
                                                           required_auto_mls=[automl.name for automl in self.automls],
                                                           runtime_constraints=self.__configuration.runtime_constraints)
        response.status = SessionStatus.SESSION_STATUS_COMPLETED
        response.dataset = self.__configuration.dataset
        response.task = self.__configuration.task

        for automl in self.automls:
            response.automls.append(automl.get_status())
            if automl.is_running():
                response.status = SessionStatus.SESSION_STATUS_BUSY
        return response
