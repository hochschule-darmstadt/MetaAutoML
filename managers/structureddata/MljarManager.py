import json
import os

import zope.interface

import grpc
import Controller_pb2
import Controller_pb2_grpc
import Adapter_pb2
import Adapter_pb2_grpc

from IAutoMLManager import IAutoMLManager
from threading import *

@zope.interface.implementer(IAutoMLManager)
class MljarManager(Thread):
    """
    Implemenation of the MLJAR AutoML functionality
    """
    name = "MLJAR"
    def __init__(self, configuration, folder_location):
        """
        Init a new instance of the AutoKerasManager
        ---
        Parameter
        1. configuration dictionary for the AutoML
        2. folder location of the training dataset
        """
        super(MljarManager, self).__init__()
        self.__configuration = configuration
        self.__file_dest = folder_location
        self.__result_json = ""
        self.__is_completed = False
        self.__status_messages = []
        return
    
    def GetAutoMlModel(self) -> Controller_pb2.GetSessionStatusResponse:
        """
        Get the generated AutoML model
        ---
        Return the AutoML model if the run is concluded
        """
        result = Controller_pb2.GetAutoMlModelResponse()
        result.name = self.__result_json["file_name"]
        with open(os.path.join(self.__result_json["file_location"], self.__result_json["file_name"]), "rb") as a:
            result.file = a.read()
        return result

    def GetStatus(self) -> Controller_pb2.AutoMLStatus:
        """
        Get the execution status of the AutoML
        ---
        Return the current AutoML status
        """
        status = Controller_pb2.AutoMLStatus()
        status.name = MljarManager.name
        if self.__is_completed == True:
            status.status = Controller_pb2.SESSION_STATUS_COMPLETED
        else:
            status.status = Controller_pb2.SESSION_STATUS_BUSY
        status.messages[:] = self.__status_messages
        return status

    def IsRunning(self) -> bool:
        """
        Check if the AutoML is currently running
        ---
        Return bool if AutoML is running => true
        """
        return not self.__is_completed

    def run(self):
        """
        AutoML task for the current run
        """
        #Open
        #with grpc.insecure_channel('localhost:50053') as channel:
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = Adapter_pb2_grpc.AdapterServiceStub(channel)
            datasetToSend = Adapter_pb2.StartAutoMLRequest()
            processJson = {"file_name": self.__configuration.dataset}
            processJson.update({"file_location": self.__file_dest})
            processJson.update({"task": self.__configuration.task})
            processJson.update({"configuration": { "target": self.__configuration.tabularConfig.target } })
            datasetToSend.process_json = json.dumps(processJson)
            for response in stub.StartAutoML(datasetToSend):
                if response.returnCode == Adapter_pb2.ADAPTER_RETURN_CODE_STATUS_UPDATE:
                    self.__status_messages.append(response.statusUpdate)
                elif response.returnCode == Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS:
                    self.__result_json = json.loads(response.outputJson)
                    self.__is_completed = True
                    return

    def GetResult(self):
        controllerResult = Controller_pb2.UploadDatasetFileResponse()
        controllerResult.name = resultJson["file_name"]
        controllerResult.content = file_zip.read()