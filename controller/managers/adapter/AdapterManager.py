from ControllerBGRPC import *
import json, logging, os, datetime
from threading import *
import asyncio
from grpclib.client import Channel
from AdapterBGRPC import *
from DataStorage import DataStorage

class AdapterManager(Thread):
    """The AdapterManager provides functionality for the training process to connect to the correct adapter and execute the training

    Args:
        Thread (_type_): _description_
    """

    def __init__(self, data_storage: DataStorage, request: "CreateTrainingRequest", automl:str, training_id: str, dataset, host: str, port: int, adapter_finished_callback) -> None:
        """Initialize a new AdapterManager

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            request (CreateTrainingRequest): The training request configuration
            automl (str): The AutoML adapter name
            training_id (str): The training id to which the found model is linked too
            dataset (_type_): The Dataset record used by this training
            host (str): The AutoML adapter ip address
            port (int): The AutoML adapter port
            blackboard (_type_): The blackboard instance for this training session
            strategy_controller (_type_): The Blackboard instance for this training session
            adapter_finished_callback (_type_): The callback function to execute when the training finishes
        """
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
        self.__model_id = self.__create_new_model_entry()

    def set_request(self, request: "CreateTrainingRequest"):
        """Set the training request object
        """
        self.__request = request

    def get_automl_name(self) -> str:
        """Get the AutoML adapter name

        Returns:
            str: The AutoML adapter name
        """
        return self.__automl

    def get_training_id(self) -> str:
        """Get the training id to which the found model is linked too

        Returns:
            str: The training id
        """
        return self.__training_id

    def is_running(self) -> bool:
        """Check if the AutoML adapter training is still running

        Returns:
            bool: True if the training is still running, False if it has ended
        """
        if self.__status == "failed" or self.__status == "completed":
            return False
        else:
            return True

    def get_status(self) -> str:
        """Get the current training process status

        Returns:
            str: The current training process status
        """
        return self.__status

    def get_status_for_blackboard(self) -> dict:
        """Get the current AutoML adapter status for the blackboard

        Returns:
            dict: The current AutoML adapter status
        """
        return {
            'status': self.__status,
            'test_score': self.__testScore,
            'runtime': self.__runtime,
            'prediction_time': self.__prediction_time,
            'model': self.__ml_model_type,
            'library': self.__ml_library
        }

    def handle_blackboard_phase_update(self):
        """Blackboard functionality called when the blackboard changes phases
        TODO: still needded?
        """
        return


    def __generate_process_request(self) -> "StartAutoMlRequest":
        """Generate AutoML training configuration

        Returns:
            StartAutoMlRequest: The GRPC request message holding the training configuration
        """
        request = StartAutoMlRequest()
        request.training_id = self.__training_id
        request.dataset_id = str(self.__dataset["_id"])
        request.user_id = self.__request.user_id
        request.dataset_path =  self.__dataset["path"]

        configuration = StartAutoMlConfiguration()
        configuration.task = self.__request.configuration.task
        configuration.runtime_limit = self.__request.configuration.runtime_limit
        configuration.metric = self.__request.configuration.metric

        request.configuration = configuration
        found, training = self.__data_storage.get_training(self.__request.user_id, self.__training_id)
        request.dataset_configuration = json.dumps(training["dataset_configuration"])

        return request

    def __create_new_model_entry(self) -> str:
        """Create the model record for this AutoML adapter

        Returns:
            str: The model record id
        """
        model_details = {
            "training_id": self.__training_id,
            "prediction_ids": [],
            "status": self.__status,
            "auto_ml_solution": self.__automl,
            "ml_model_type": "",
            "ml_library": "",
            "path": "",
            "test_score": 0,
            "prediction_time": 0,
            "runtime_profile": {
                "start_time": datetime.datetime.now(),
                "end_time": datetime.datetime.now(),
            },
            "status_messages": [],
            "explanation": {},
            "lifecycle_state": "active",
            "carbon_footprint": {}
            }
        return self.__data_storage.create_model(self.__request.user_id, model_details)

    def cancel_adapter(self):
        print("canceling me")
        model_details = {
            "status": "aborted"
        }
        self.__adapter_finished_callback(self.__training_id, self.__request.user_id, self.__model_id, model_details, self)
        return

    async def __read_grpc_connection(self):
        """Open a new connection to the AutoML adapter and start the training process and read all Status messages until the process concludes
        """
        try:  # Run until server closes connection
            import datetime
            channel = Channel(host=self.__host, port=self.__port)
            service = AdapterServiceStub(channel=channel)
            self.__log.debug(f"run: connecting to AutoML Adapter {self.__host}:{self.__port}")
            response: StartAutoMlResponse = await service.start_auto_ml(self.__generate_process_request())
            self.__session_id = response.session_id
            await asyncio.sleep(5)

            while True:
                await asyncio.sleep(0.1)
                request = GetAutoMlStatusRequest()
                request.session_id = self.__session_id
                response: GetAutoMlStatusResponse = await service.get_auto_ml_status(request)
                # Send request WATCH OUT THIS IS A LOOP REQUEST Check out for normal request
                # https://grpc.io/docs/languages/python/quickstart/#update-the-client
                if response.return_code == AdapterReturnCode.ADAPTER_RETURN_CODE_PENDING:
                    continue
                if response.return_code == AdapterReturnCode.ADAPTER_RETURN_CODE_STATUS_UPDATE:
                    self.__status_messages.append(response.status_update)
                    self.__data_storage.update_model(self.__request.user_id, self.__model_id, {"status_messages": self.__status_messages})
                elif response.return_code == AdapterReturnCode.ADAPTER_RETURN_CODE_SUCCESS:
                    channel.close()
                    self.__path = response.path
                    self.__status = "completed"
                    self.__testScore = response.test_score
                    self.__prediction_time = response.prediction_time
                    self.__ml_model_type = response.ml_model_type
                    self.__ml_library = response.ml_library
                    self.__carbon_footprint = response.emission_profile.to_dict(casing=betterproto.Casing.SNAKE)
                    found, model = self.__data_storage.get_model(self.__request.user_id, self.__model_id)
                    model_details = {
                        "status": self.__status,
                        "ml_model_type": self.__ml_model_type,
                        "ml_library": self.__ml_library,
                        "path": self.__path,
                        "prediction_time": self.__prediction_time,
                        "test_score": self.__testScore,
                        "runtime_profile": model["runtime_profile"],
                        "carbon_footprint": self.__carbon_footprint
                    }
                    model_details["runtime_profile"]["end_time"] = datetime.datetime.now()

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
        """Listen to the started AutoML process until termination
        """
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)
        #loop.run_until_complete(self.__read_grpc_connection())
        #loop.close()
        asyncio.run(self.__read_grpc_connection())


    def _generate_test_json(self) -> dict:
        """Generate AutoML configuration for the explanation request

        Returns:
            dict: AutoML explanation configuration
        """
        found, training = self.__data_storage.get_training(self.__request.user_id, self.__training_id)
        test_json = {
            "training_id": self.__training_id,
            "user_id": self.__request.user_id,
            "dataset_id": str(self.__dataset["_id"]),
            "configuration": {
                "task": self.__request.configuration.task,
                "target": self.__request.configuration.target
            },
            "dataset_configuration": json.dumps(training["dataset_configuration"]),
            "dataset_path": self.__dataset["path"]
        }
        return test_json


    def explain_model(self, data):
        """Explain a specific model.
        This loads the model and returns the output of the "predict_proba()" function in case of tabular classification.
        If the ML task is tabular regression the output of "predict()" is returned instead.

        Args:
            data (_type_): Data to process to compute probabilities within the AutoML adapter

        Returns:
            _type_: List of produced outputs
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
            request.process_json = json.dumps(process_json)
            request.data = data
            response = loop.run_until_complete(service.explain_model(request))
            channel.close()
            return response
        except grpclib.GRPCError as rpc_error:
            print(f"Received unknown RPC error: code={rpc_error.message} message={rpc_error.details()}")
