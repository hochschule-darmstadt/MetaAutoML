
from AdapterManagerAgent import AdapterManagerAgent
from ControllerBGRPC import *
import json, logging, os
from threading import *
import asyncio
from grpclib.client import Channel
from AdapterBGRPC import *
from DataStorage import DataStorage
from AdapterBGRPC import *
from betterproto.grpc.util.async_channel import AsyncChannel

class AdapterPredictionManager(Thread):

    def __init__(self, data_storage: DataStorage, request: "ModelPredictRequest", request_configuration: dict, user_identifier: str, automl:str, training_identifier: str, host: str, port: int, prediction_identifier: str, adapter_finished_callback) -> None:
        
        super(AdapterPredictionManager, self).__init__()
        self.__log = logging.getLogger('AdapterPredictionManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__data_storage = data_storage
        self.__request = request
        self.__request_configuration = request_configuration
        self.__prediction_identifier = prediction_identifier
        self.__automl = automl
        self.__training_identifier = training_identifier
        self.__user_identifier = user_identifier
        self.__host = host
        self.__port = port
        self.__status_messages = []
        self.__adapter_finished_callback = adapter_finished_callback
        self.__status = "started"
        self.__testScore = 0
        self.__runtime = 0
        self.__prediction_time = 0
        self.__ml_model_type = ""
        self.__ml_library = ""

    def is_running(self):
        if self.__status == "failed" or self.__status == "completed":
            return False
        else:
            return True

    def get_status(self):
        return self.__status

    async def __read_grpc_connection(self):
        try:  # Run until server closes connection
            self.__status = "busy"
            # Append model_id to dataset
            with self.__data_storage.lock():
                found, prediction_dataset = self.__data_storage.get_prediction_dataset(self.__request.user_identifier, self.__request.prediction_dataset_identifier)
                predicitons = prediction_dataset["predictions"]
                predicitons[self.__prediction_identifier]["status"] = "busy"
                self.__data_storage.update_prediction_dataset(self.__request.user_identifier, self.__request.prediction_dataset_identifier, {"predictions": predicitons})


            request = TestAdapterRequest()
            process_json = self.__request_configuration
            request.process_json = json.dumps(process_json)
            channel = Channel(host=self.__host, port=self.__port)
            service = AdapterServiceStub(channel=channel)
            self.__log.debug(f"run: connecting to AutoML Adapter {self.__host}:{self.__port}")
            
            response = await service.test_adapter(request)
                # Send request WATCH OUT THIS IS A LOOP REQUEST Check out for normal request
                # https://grpc.io/docs/languages/python/quickstart/#update-the-client
            print("")
        except Exception as rpc_error:
            #print(f"Received unknown RPC error: code={rpc_error.message} message={rpc_error.details()}")
            print("Connection failed to adapter")
            self.__status = "failed"
            model_details = {
                "status": self.__status
                }
            self.__adapter_finished_callback(self.__training_identifier, self.__request.user_identifier, self.__model_identifier, model_details, self)

    
    def run(self):
        """
        Listen to the started AutoML process until termination
        ---
        Parameter
        """
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)
        #loop.run_until_complete(self.__read_grpc_connection())
        #loop.close()
        asyncio.run(self.__read_grpc_connection())
