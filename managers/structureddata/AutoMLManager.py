import json
import os

import zope.interface
import grpc
import Controller_pb2
import Adapter_pb2
import Adapter_pb2_grpc

from IAutoMLManager import IAutoMLManager
from threading import *
from abc import ABC


@zope.interface.implementer(IAutoMLManager)
class AutoMLManager(ABC, Thread):
    """
    Base implementation of the  AutoML functionality
    """

    def __init__(self, configuration, folder_location, automl_service_host, automl_service_port):
        """
        Init a new instance of the abstract class AutoMLManager
        ---
        Parameter
        1. configuration dictionary for the AutoML
        2. folder location of the training dataset
        """
        super(AutoMLManager, self).__init__()
        self._configuration = configuration
        self.__file_dest = folder_location
        self.__result_json = ""
        self.__is_completed = False
        self.__status_messages = []
        self.__last_status = Controller_pb2.SESSION_STATUS_BUSY

        self.__AUTOML_SERVICE_HOST = automl_service_host
        self.__AUTOML_SERVICE_PORT = automl_service_port

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

    def get_status(self) -> Controller_pb2.AutoMLStatus:
        """
        Get the execution status of the AutoML
        ---
        Return the current AutoML status
        """
        status = Controller_pb2.AutoMLStatus()
        status.name = self.name
        status.status = self.__last_status
        status.messages[:] = self.__status_messages
        return status

    def is_running(self) -> bool:
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
        automl_ip = os.getenv(self.__AUTOML_SERVICE_HOST)
        automl_port = os.getenv(self.__AUTOML_SERVICE_PORT)

        print(f"connecting to {self.name}: {automl_ip}:{automl_port}")

        with grpc.insecure_channel(f"{automl_ip}:{automl_port}") as channel:  # Connect to Adapter
            stub = Adapter_pb2_grpc.AdapterServiceStub(channel)  ## Create Interface Stub

            request = Adapter_pb2.StartAutoMLRequest()  ## Request Object
            process_json = self._generate_process_json()
            request.processJson = json.dumps(process_json)

            self._run_server_until_connection_closed(stub, request)

    def _generate_process_json(self):
        process_json = {"file_name": self._configuration.dataset}
        process_json.update({"file_location": self.__file_dest})
        process_json.update({"task": self._configuration.task})
        process_json.update(
            {"tabular_configuration": {"target": {"target": self._configuration.tabularConfig.target.target,
                                                  "type": self._configuration.tabularConfig.target.type},
                                       "features": dict(self._configuration.tabularConfig.features)}})
        process_json.update({"file_configuration": dict(self._configuration.fileConfiguration)})
        process_json.update({"runtime_constraints":
                                 {"runtime_limit": self._configuration.runtimeConstraints.runtime_limit,
                                  "max_iter": self._configuration.runtimeConstraints.max_iter}})
        return process_json

    def _run_server_until_connection_closed(self, stub, dataset_to_send):
        try:  # Run until server closes connection
            for response in stub.StartAutoML(
                    dataset_to_send):  # Send request WATCH OUT THIS IS A LOOP REQUEST Check out for normal request https://grpc.io/docs/languages/python/quickstart/#update-the-client
                if response.returnCode == Adapter_pb2.ADAPTER_RETURN_CODE_STATUS_UPDATE:
                    self.__status_messages.append(response.statusUpdate)
                elif response.returnCode == Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS:
                    self.__result_json = json.loads(response.outputJson)
                    self.__is_completed = True
                    self.__last_status = Controller_pb2.SESSION_STATUS_COMPLETED
                    return
        except grpc.RpcError as rpc_error:
            print(f"Received unknown RPC error: code={rpc_error.code()} message={rpc_error.details()}")
            self.__is_completed = True
            self.__last_status = Controller_pb2.SESSION_STATUS_FAILED
