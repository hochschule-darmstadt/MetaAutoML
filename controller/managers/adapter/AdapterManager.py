
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

class AdapterManager(Thread):

    def __init__(self, data_storage: DataStorage, request: "CreateTrainingRequest", automl:str, training_id: str, dataset, host: str, port: int, blackboard, strategy_controller, adapter_finished_callback) -> None:
        
        super(AdapterManager, self).__init__()
        self.__log = logging.getLogger('AdapterManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__data_storage = data_storage
        self.__request = request

        self.__automl = automl
        self.__training_id = training_id
        self.__dataset = dataset
        self.__host = host
        self.__port = port
        self.__status_messages = []
        self.__adapter_finished_callback = adapter_finished_callback
        self.__status = "busy"
        self.__testScore = 0
        self.__runtime = 0
        self.__prediction_time = 0
        self.__ml_model_type = ""
        self.__ml_library = ""
        self.__blackboard = blackboard 
        self.__strategy_controller = strategy_controller
        self.__model_id = self.__create_new_model_entry()

        self.__adapter_agent = AdapterManagerAgent(self.__blackboard, self.__strategy_controller, self)

    def get_automl_name(self):
        return self.__automl

    def get_training_id(self):
        return self.__training_id

    def is_running(self):
        if self.__status == "failed" or self.__status == "completed":
            return False
        else:
            return True

    def get_status(self):
        return self.__status

    def get_status_for_blackboard(self):

        return {
            'status': self.__status,
            'test_score': self.__testScore,
            'runtime': self.__runtime,
            'prediction_time': self.__prediction_time,
            'model': self.__ml_model_type,
            'library': self.__ml_library
        }

    def handle_blackboard_phase_update(self):
        return

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
            "training_id": self.__training_id,
            "dataset_id": str(self.__dataset["_id"]),
            "file_name": self.__dataset["file_name"],
            "file_location": self.__dataset["path"],
            "task": self.__request.task,
            "configuration": json.loads(self.__request.configuration),
            "dataset_configuration": json.loads(self.__request.dataset_configuration),
            "runtime_constraints": json.loads(self.__request.runtime_constraints),
            "test_configuration": test_config,
            "file_configuration": self.__dataset["file_configuration"],
            "metric": self.__request.metric,
            "user_id": self.__request.user_id
        }

    def __create_new_model_entry(self):
        model_details = {
            "automl_name": self.__automl,
            "training_id": self.__training_id,
            "dataset_id": str(self.__dataset["_id"]),
            "path": "",
            "test_score": 0,
            "runtime": 0,
            "ml_model_type": "",
            "ml_library": "", 
            "status": self.__status,
            "status_messages": [],
            "prediction_time": 0,
            "start_time": datetime.now(),
            "end_time": 0,
            "explanation": ""
            }
        return self.__data_storage.create_model(self.__request.user_id, model_details)
    
    async def __read_grpc_connection(self):
        try:  # Run until server closes connection
            self.__status = "busy"
            # Append model_id to dataset
            with self.__data_storage.lock():
                self.__data_storage.update_model(self.__request.user_id, self.__model_id, {"status": self.__status})
                found, dataset = self.__data_storage.get_dataset(self.__request.user_id, str(self.__dataset["_id"]))
                self.__data_storage.update_dataset(self.__request.user_id, str(self.__dataset["_id"]), { "models": dataset["models"] + [self.__model_id] }, False)

            request = StartAutoMlRequest()
            process_json = self.__generate_process_json()
            request.process_json = json.dumps(process_json)
            channel = Channel(host=self.__host, port=self.__port)
            service = AdapterServiceStub(channel=channel)
            self.__log.debug(f"run: connecting to AutoML Adapter {self.__host}:{self.__port}")
            response: StartAutoMlResponse = await service.start_auto_ml(request)
            self.__session_id = response.session_id
            await asyncio.sleep(5)

            while True:
                await asyncio.sleep(0.2)
                request = GetAutoMlStatusRequest()
                request.session_id = self.__session_id
                response: GetAutoMlStatusResponse = await service.get_auto_ml_status(request)
                # Send request WATCH OUT THIS IS A LOOP REQUEST Check out for normal request
                # https://grpc.io/docs/languages/python/quickstart/#update-the-client
                if response.return_code == AdapterReturnCode.ADAPTER_RETURN_CODE_PENDING:
                    continue
                if response.return_code == AdapterReturnCode.ADAPTER_RETURN_CODE_STATUS_UPDATE:
                    self.__status_messages.append(response.status_update)
                    self.__runtime = response.runtime
                    self.__data_storage.update_model(self.__request.user_id, self.__model_id, {"status": "busy", "status_messages": self.__status_messages, "runtime": self.__runtime})
                elif response.return_code == AdapterReturnCode.ADAPTER_RETURN_CODE_SUCCESS:
                    channel.close()
                    self.__result_json = json.loads(response.output_json)
                    self.__status = "completed"
                    self.__testScore = response.test_score
                    self.__runtime = response.runtime
                    self.__prediction_time = response.prediction_time
                    self.__ml_model_type = response.model
                    self.__ml_library = response.library

                    model_details = {
                        "path": os.path.join(self.__result_json["file_location"], self.__result_json["file_name"]),
                        "test_score": self.__testScore,
                        "runtime": self.__runtime,
                        "ml_model_type": self.__ml_model_type,
                        "ml_library": self.__ml_library,
                        "prediction_time": self.__prediction_time,
                        "status": self.__status,
                        "end_time": datetime.now()
                    }
                    self.__adapter_finished_callback(self.__training_id, self.__request.user_id, self.__model_id, model_details, self)
                    return

        except Exception as rpc_error:
            #print(f"Received unknown RPC error: code={rpc_error.message} message={rpc_error.details()}")
            print(rpc_error)
            channel.close()
            print("Connection failed to adapter")
            self.__status = "failed"
            model_details = {
                "status": self.__status
                }
            self.__adapter_finished_callback(self.__training_id, self.__request.user_id, self.__model_id, model_details, self)

    
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


    def _generate_test_json(self,):
        """
        Generate AutoML configuration JSON
        ---
        Return configuration JSON
        """
        return {
            "training_id": self.__training_id,
            "user_id": self.__request.user_id,
            "dataset_id": str(self.__dataset["_id"]),
            "task": self.__request.task,
            "configuration": self.__request.configuration,
            "dataset_configuration": self.__request.dataset_configuration,
            "runtime_constraints": self.__request.runtime_constraints,
            "test_configuration": json.loads(self.__request.test_configuration),
            "file_configuration": self.__dataset["file_configuration"],
            "file_location": self.__dataset["path"],
            "file_name": self.__dataset["file_name"],
            "metric": self.__request.metric
        }




    def explain_model(self, data):
        """
        Explain a specific model.
        This loads the model and returns the output of the "predict_proba()" function in case of tabular classification.
        If the ML task is tabular regression the output of "predict()" is returned instead.
        ---
        Parameter
        data: Data to process
        training_id: training id to use
        ---
        Return
        List of produced outputs
        """
        print(f"connecting {self.__host}:{self.__port}")
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            channel = Channel(host=self.__host, port=self.__port)
            service = AdapterServiceStub(channel=channel)
            request = ExplainModelRequest()  # Request Object
            request.session_id = self.__session_id
            process_json = self._generate_test_json()
            process_json["test_configuration"]["method"] = 1
            process_json["test_configuration"]["split_ratio"] = 0
            request.process_json = json.dumps(process_json)
            request.data = data
            response = loop.run_until_complete(service.explain_model(request))
            channel.close()
            response = response
            return response
        except grpclib.GRPCError as rpc_error:
            print(f"Received unknown RPC error: code={rpc_error.message} message={rpc_error.details()}")