import json
import os
import grpc
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

    def __init__(self, configuration: "StartAutoMlProcessRequest", folder_location, automl_service_host, automl_service_port, session_id, username, data_storage, callback=None):
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
        self.__last_status = "Busy"

        self.__AUTOML_SERVICE_HOST = automl_service_host
        self.__AUTOML_SERVICE_PORT = automl_service_port

        self.__callback = callback

        self.__username = username
        self.__data_storage = data_storage

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

        print(f"connecting to {self.name}: {self.__AUTOML_SERVICE_HOST}:{self.__AUTOML_SERVICE_PORT}")

        with grpc.insecure_channel(f"{self.__AUTOML_SERVICE_HOST}:{self.__AUTOML_SERVICE_PORT}") as channel:  # Connect to Adapter
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

        print(f"connecting to {self.name}: {self.__AUTOML_SERVICE_HOST}:{self.__AUTOML_SERVICE_PORT}")

        with grpc.insecure_channel(f"{self.__AUTOML_SERVICE_HOST}:{self.__AUTOML_SERVICE_PORT}") as channel:  # Connect to Adapter
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

        test_config = json.loads(self._configuration.test_configuration)

    
        #if test_config.update("split_ratio": 0):
        test_config.update({"split_ratio": 0.8})
        test_config.update({"random_state": 42})

        return {
            "session_id": self.__session_id,
            "file_name": self._configuration.dataset,
            "file_location": self.__file_dest,
            "task": self._configuration.task,
            "configuration": json.loads(self._configuration.configuration),
            "dataset_configuration": json.loads(self._configuration.dataset_configuration),
            "runtime_constraints": json.loads(self._configuration.runtime_constraints),
            "test_configuration": test_config,
            "file_configuration": json.loads(self._configuration.file_configuration),
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
            #create new model
            model_details = {
                "automl_name": self.name,
                "session_id": self.__session_id,
                "path": "",
                "test_score": 0,
                "validation_score": 0,
                "runtime": 0,
                "model": "",
                "library": "", 
                "status": "busy",
                "status_messages": [],
                "prediction_time": 0
                }
            _mdl_id = self.__data_storage.insert_model(self.__username, model_details)
            for response in stub.StartAutoML(dataset_to_send):
                # Send request WATCH OUT THIS IS A LOOP REQUEST Check out for normal request
                # https://grpc.io/docs/languages/python/quickstart/#update-the-client

                if response.returnCode == Adapter_pb2.ADAPTER_RETURN_CODE_STATUS_UPDATE:
                    self.__status_messages.append(response.statusUpdate)
                    self.__runtime = response.runtime
                    self.__data_storage.update_model(self.__username, _mdl_id, {"status": "busy", "status_messages": self.__status_messages, "runtime": response.runtime})
                elif response.returnCode == Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS:
                    self.__result_json = json.loads(response.outputJson)
                    self.__is_completed = True
                    self.__last_status = "completed"
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
                        model_details = {
                            "automl_name": self.name,
                            "session_id": self.__session_id,
                            "path": os.path.join(self.__result_json["file_location"], self.__result_json["file_name"]),
                            "test_score": self.__testScore,
                            "validation_score": self.__validationScore,
                            "runtime": self.__runtime,
                            "model": self.__model,
                            "library": self.__library,
                            "prediction_time": self.__predictiontime,
                            "status": self.__last_status
                        }
                        self.__callback(self.__session_id, _mdl_id, model_details)

                    return
        except grpc.RpcError as rpc_error:
            print(f"Received unknown RPC error: code={rpc_error.code()} message={rpc_error.details()}")
            self.__is_completed = True
            self.__last_status = "failed"
            model_details = {
                "automl_name": self.name,
                "session_id": self.__session_id,
                "path": "",
                "test_score": 0,
                "validation_score": 0,
                "runtime": 0,
                "model": "",
                "library": "",
                "prediction_time": 0,
                "status": self.__last_status
                }
            self.__data_storage.update_model(self.__username, _mdl_id, {"status": "Failed"})
            self.__callback(self.__session_id, _mdl_id, model_details)
                        