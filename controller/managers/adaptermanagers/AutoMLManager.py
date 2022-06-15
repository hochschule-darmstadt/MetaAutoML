import json
import os

import zope.interface
import Adapter_pb2
import Adapter_pb2_grpc

from IAutoMLManager import IAutoMLManager
from threading import *
from abc import ABC
from Controller_bgrpc import *


@zope.interface.implementer(IAutoMLManager)
class AutoMLManager(ABC, Thread):
    """
    Base implementation of the  AutoML functionality
    """

    def __init__(self, configuration: "StartAutoMlProcessRequest", folder_location, automl_service_host, automl_service_port, session_id, callback=None):
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
        self.__session_id = session_id
        self.__result_json = {}
        self.__is_completed = False
        self.__status_messages = []
        self.__testScore = 0.0
        self.__validationScore = 0.0
        self.__runtime = 0
        self.__predictiontime = 0
        self.__model = ""
        self.__library = ""
        self.__last_status = SessionStatus.SESSION_STATUS_BUSY

        self.__AUTOML_SERVICE_HOST = automl_service_host
        self.__AUTOML_SERVICE_PORT = automl_service_port

        self.__callback = callback

    def get_automl_model(self) -> GetSessionStatusResponse:
        """
        Get the generated AutoML model
        ---
        Return the AutoML model if the run is concluded
        """
        result = GetAutoMlModelResponse()
        result.name = self.__result_json["file_name"]
        with open(os.path.join(self.__result_json["file_location"], self.__result_json["file_name"]), "rb") as a:
            result.file = a.read()
        return result

    def get_status(self) -> "AutoMlStatus":
        """
        Get the execution status of the AutoML
        ---
        Return the current AutoML status
        """
        status = AutoMlStatus()
        status.name = self.name
        status.status = self.__last_status
        status.messages[:] = self.__status_messages
        status.testScore = self.__testScore
        status.validationScore = self.__validationScore
        status.runtime = self.__runtime
        status.predictiontime = self.__predictiontime
        status.model = self.__model
        status.library = self.__library
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
            stub = Adapter_pb2_grpc.AdapterServiceStub(channel)  # Create Interface Stub

            request = Adapter_pb2.StartAutoMLRequest()  # Request Object
            process_json = self._generate_process_json()
            request.processJson = json.dumps(process_json)

            self._run_server_until_connection_closed(stub, request)

    def testSolution(self, test_data, session_id):
        """
        Init a new instance of the specific AutoMLManager
        ---
        Parameter
        1. configuration dictionary
        2. folder location of the dataset
        3. session id to use
        ---
        Return a new specific AutoML Manager
        """
        automl_ip = os.getenv(self.__AUTOML_SERVICE_HOST)
        automl_port = os.getenv(self.__AUTOML_SERVICE_PORT)

        print(f"connecting to {self.name}: {automl_ip}:{automl_port}")

        with grpc.insecure_channel(f"{automl_ip}:{automl_port}") as channel:  # Connect to Adapter
            stub = Adapter_pb2_grpc.AdapterServiceStub(channel)  # Create Interface Stub

            request = Adapter_pb2.TestAdapterRequest()  # Request Object
            process_json = self._generate_process_json()
            process_json["session_id"] = session_id
            process_json["test_configuration"]["method"] = 1
            process_json["test_configuration"]["split_ratio"] = 0
            request.processJson = json.dumps(process_json)
            request.testData = test_data

            try:
                return stub.TestAdapter(request)

            except grpc.RpcError as rpc_error:
                print(f"Received unknown RPC error: code={rpc_error.code()} message={rpc_error.details()}")

    def _generate_process_json(self,):
        """
        Generate AutoML configuration JSON
        ---
        Return configuration JSON
        """

        if self._configuration.test_config.split_ratio == 0:
            self._configuration.test_config.split_ratio = 0.8
            self._configuration.test_config.random_state = 42

        return {
            "session_id": self.__session_id,
            "file_name": self._configuration.dataset,
            "file_location": self.__file_dest,
            "task": self._configuration.task,
            "test_configuration": {
                "split_ratio": self._configuration.test_config.split_ratio,
                "method": self._configuration.test_config.method,
                "random_state": self._configuration.test_config.random_state
            },
            "tabular_configuration": {
                "target": {
                    "target": self._configuration.tabular_config.target.target,
                    "type": self._configuration.tabular_config.target.type
                },
                "features": dict(self._configuration.tabular_config.features)
            },
            "file_configuration": dict(self._configuration.file_configuration),
            "runtime_constraints": {
                "runtime_limit": self._configuration.runtime_constraints.runtime_limit * 60,
                "max_iter": self._configuration.runtime_constraints.max_iter
            },
            "metric": self._configuration.metric
        }

    def _run_server_until_connection_closed(self, stub, dataset_to_send):
        """
        Listen to the started AutoML process until termination
        ---
        Parameter
        1. connection stub
        2. initial Start AutoML request
        """
        try:  # Run until server closes connection
            for response in stub.StartAutoML(dataset_to_send):
                # Send request WATCH OUT THIS IS A LOOP REQUEST Check out for normal request
                # https://grpc.io/docs/languages/python/quickstart/#update-the-client

                if response.returnCode == Adapter_pb2.ADAPTER_RETURN_CODE_STATUS_UPDATE:
                    self.__status_messages.append(response.statusUpdate)
                    self.__runtime = response.runtime
                elif response.returnCode == Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS:
                    self.__result_json = json.loads(response.outputJson)
                    self.__is_completed = True
                    self.__last_status = SessionStatus.SESSION_STATUS_COMPLETED
                    self.__testScore = response.testScore
                    self.__validationScore = response.validationScore
                    self.__runtime = response.runtime
                    self.__predictiontime = response.predictiontime
                    self.__model = response.model
                    self.__library = response.library

                    # notify automl starter process that we finished
                    if self.__callback is not None:
                        # NOTE: this depends on subclass implementing the field "name"
                        # TODO: implement better automl naming mechanism
                        automl_name = self.name
                        self.__callback(self.__session_id, automl_name, self.__result_json)

                    return
        except grpc.RpcError as rpc_error:
            print(f"Received unknown RPC error: code={rpc_error.code()} message={rpc_error.details()}")
            self.__is_completed = True
            self.__last_status = SessionStatus.SESSION_STATUS_FAILED
