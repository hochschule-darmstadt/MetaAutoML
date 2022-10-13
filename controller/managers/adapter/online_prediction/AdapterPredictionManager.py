
from AdapterManagerAgent import AdapterManagerAgent
from ControllerBGRPC import *
import json, logging, os,datetime
from threading import *
import asyncio
from grpclib.client import Channel
from AdapterBGRPC import *
from DataStorage import DataStorage
from AdapterBGRPC import *
from betterproto.grpc.util.async_channel import AsyncChannel

class AdapterPredictionManager(Thread):

    def __init__(self, data_storage: DataStorage, request_configuration: dict, user_id: str, prediction_id: str, host: str, port: int) -> None:
        
        super(AdapterPredictionManager, self).__init__()
        self.__log = logging.getLogger('AdapterPredictionManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__data_storage = data_storage
        self.__request_configuration = request_configuration
        self.__prediction_id = prediction_id
        self.__user_id = user_id
        self.__host = host
        self.__port = port
        self.__status = "started"

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

            request = PredictModelRequest()
            process_json = self.__request_configuration
            request.process_json = json.dumps(process_json)
            channel = Channel(host=self.__host, port=self.__port)
            service = AdapterServiceStub(channel=channel)
            self.__log.debug(f"run: connecting to AutoML Adapter {self.__host}:{self.__port}")
            

            response = await service.predict_model(request)
            found, prediction = self.__data_storage.get_prediction(self.__user_id, self.__prediction_id)
            prediction_details = { 
                "status": "completed", 
                "runtime_profile": prediction["runtime_profile"],
                "prediction_path": response.result_path 
            }
            prediction_details["runtime_profile"]["end_time"] = datetime.datetime.now()
            with self.__data_storage.lock():
                self.__data_storage.update_prediction(self.__user_id, self.__prediction_id, prediction_details)
            return
        except Exception as rpc_error:
            #print(f"Received unknown RPC error: code={rpc_error.message} message={rpc_error.details()}")
            print("Connection failed to adapter")
            with self.__data_storage.lock():
                self.__data_storage.update_prediction(self.__user_id, self.__prediction_id, { "status": "failed" })
            return

    
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
