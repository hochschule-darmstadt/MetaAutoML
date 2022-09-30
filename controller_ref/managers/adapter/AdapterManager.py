
from ControllerBGRPC import *
import json, logging, os
from threading import *
import asyncio
from grpclib.client import Channel
from AdapterBGRPC import *
from DataStorage import DataStorage
from AdapterBGRPC import *

class AdapterManager():

    def __init__(self, data_storage: DataStorage, request: "CreateTrainingRequest", automl:str, training_identifier: str, dataset, host: str, port: int) -> None:
        
        super(AdapterManager, self).__init__()
        self.__log = logging.getLogger('AdapterManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__data_storage = data_storage
        self.__request = request
        self.__automl = automl
        self.__training_identifier = training_identifier
        self.__dataset = dataset
        self.__host = host
        self.__port = port

    def __generate_process_json(self):
        """
        Generate AutoML configuration JSON
        ---
        Return configuration JSON
        """

        test_config = json.loads(self.__request.test_configuration)

    
        #if test_config.update("split_ratio": 0):
        test_config.update({"split_ratio": 0.8})
        test_config.update({"random_state": 42})

        return {
            "training_identifier": self.__training_identifier,
            "file_name": self.__dataset["file_name"],
            "file_location": self.__dataset["path"],
            "task": self.__request.task,
            "configuration": json.loads(self.__request.configuration),
            "dataset_configuration": json.loads(self.__request.dataset_configuration),
            "runtime_constraints": json.loads(self.__request.runtime_constraints),
            "test_configuration": test_config,
            "file_configuration": json.loads(self.__dataset["file_configuration"]),
            "metric": self.__request.metric,
            "user_identifier": self.__request.user_identifier
        }

    def __create_new_model_entry(self):
        model_details = {
            "automl_name": self.__automl,
            "training_identifier": self.__training_identifier,
            "dataset_identifier": str(self.__dataset["_id"]),
            "path": "",
            "test_score": 0,
            "runtime": 0,
            "ml_model_type": "",
            "ml_library": "", 
            "status": "busy",
            "status_messages": [],
            "prediction_time": 0,
            "start_time": datetime.now(),
            "end_time": 0,
            "explanation": ""
            }
        return self.__data_storage.create_model(self.__request.user_identifier, model_details)
    
    
    async def run_new_adapter_training(self):
        """
        Listen to the started AutoML process until termination
        ---
        Parameter
        """
        channel = Channel(host=self.__host, port=self.__port)
        service = AdapterServiceStub(channel=channel)
        try:  # Run until server closes connection
            self.__model_identifier = self.__create_new_model_entry()

            # Append model_id to dataset
            found, dataset = self.__data_storage.get_dataset(self.__request.user_identifier, str(self.__dataset["_id"]))
            self.__data_storage.update_dataset(self.__request.user_identifier, str(self.__dataset["_id"]), { "models": dataset["models"] + [self.__model_identifier] }, False)

            request = StartAutoMlRequest()
            process_json = self.__generate_process_json()
            request.process_json = json.dumps(process_json)
            self.__log.debug(f"run: connecting to AutoML Adapter {self.__host}:{self.__port}")
            async for response in service.start_auto_ml(request):
                # Send request WATCH OUT THIS IS A LOOP REQUEST Check out for normal request
                # https://grpc.io/docs/languages/python/quickstart/#update-the-client

                if response.return_code == AdapterReturnCode.ADAPTER_RETURN_CODE_STATUS_UPDATE:
                    self.__status_messages.append(response.statusUpdate)
                    self.__runtime = response.runtime
                    self.__data_storage.UpdateModel(self.__username, _mdl_id, {"status": "busy", "status_messages": self.__status_messages, "runtime": response.runtime})
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
                            "training_id": self.__training_id,
                            "path": os.path.join(self.__result_json["file_location"], self.__result_json["file_name"]),
                            "test_score": self.__testScore,
                            "validation_score": self.__validationScore,
                            "runtime": self.__runtime,
                            "model": self.__model,
                            "library": self.__library,
                            "prediction_time": self.__predictiontime,
                            "status": self.__last_status,
                            "end_time": datetime.now()
                        }
                        self.__callback(self.__training_id, _mdl_id, model_details)

                    return
        except grpc.RpcError as rpc_error:
            print(f"Received unknown RPC error: code={rpc_error.code()} message={rpc_error.details()}")
            self.__is_completed = True
            self.__last_status = "failed"
            model_details = {
                "automl_name": self.name,
                "training_id": self.__training_id,
                "path": "",
                "test_score": 0,
                "validation_score": 0,
                "runtime": 0,
                "model": "",
                "library": "",
                "prediction_time": 0,
                "status": self.__last_status
                }
            self.__callback(self.__training_id, _mdl_id, model_details)
        finally:
            channel.close()
                        