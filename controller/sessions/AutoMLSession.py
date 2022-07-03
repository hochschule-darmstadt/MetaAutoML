import os
from pathlib import Path
import pandas as pd

import Controller_pb2
from JsonUtil import get_config_property
from IAutoMLManager import IAutoMLManager


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
        self.__configuration = configuration
        self.automls = []

    def add_automl_to_session(self, automl: IAutoMLManager):
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

    def get_automl_model(self, request) -> Controller_pb2.GetAutoMlModelResponse:
        """
        Get the AutoML model of requested AutoML
        ---
        Parameter
        1. request: info about what AutoML the model is to be retrieved
        ---
        Return AutoML model as Controller_pb2.GetAutoMlModelResponse
        """
        for automl in self.automls:
            if automl.name == request.autoMl:
                return automl.get_automl_model()

    def get_session_status(self) -> Controller_pb2.GetSessionStatusResponse:
        """
        Get the session status
        ---
        Return the session status as Controller_pb2.GetSessionStatusResponse
        """
        target_config = Controller_pb2.AutoMLTarget(target=self.__configuration.tabularConfig.target.target,
                                                    type=self.__configuration.tabularConfig.target.type)
        tabular_config = Controller_pb2.AutoMLConfigurationTabularData(
            target=target_config, features=dict(self.__configuration.tabularConfig.features))

        runtime_constraints = Controller_pb2.AutoMLRuntimeConstraints(
            runtime_limit=self.__configuration.runtimeConstraints.runtime_limit,
            max_iter=self.__configuration.runtimeConstraints.max_iter)

        response = Controller_pb2.GetSessionStatusResponse(tabularConfig=tabular_config,
                                                           requiredAutoMLs=[automl.name for automl in self.automls],
                                                           runtimeConstraints=runtime_constraints,)
        response.status = Controller_pb2.SESSION_STATUS_COMPLETED
        response.dataset = self.__configuration.dataset
        response.task = self.__configuration.task

        for automl in self.automls:
            response.automls.append(automl.get_status())
            if automl.is_running():
                response.status = Controller_pb2.SESSION_STATUS_BUSY
        return response
