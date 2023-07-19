import uuid
from AdapterManager import *
from AdapterBGRPC import *
from dependency_injector.wiring import inject, Provide

class AdapterScheduler:
    """The AdapterScheduler manages all adapter processes, it create new AdapterManagers on-demand for new training or predictions, and provide functionality to query the correct AdapterManager
    """

    def __init__(self) -> None:
        """Initialize a new AdapterScheduler, is managed by dependency injection"""
        self.__adapter_managers: dict[str, AdapterManager] = {}
        return

    @inject
    async def start_auto_ml(self, start_auto_ml_request: "StartAutoMlRequest", adapter_manager: AdapterManager = Provide["managers.adapter_manager"]) -> "StartAutoMlResponse":
        """Request for the adapter to start a new training session

        Args:
            start_auto_ml_request (StartAutoMlRequest): The Grpc request message
            adapter_manager (AdapterManager, optional): Injected AdapterManager instance providing the adapter functionality. Defaults to Provide["managers.adapter_manager"].

        Returns:
            StartAutoMlResponse: The Grpc response message
        """
        new_session_id = str(uuid.uuid4())
        self.__adapter_managers[new_session_id] = adapter_manager
        adapter_manager.start_auto_ml(start_auto_ml_request, new_session_id)
        adapter_manager.start()
        response = StartAutoMlResponse()
        response.session_id = new_session_id
        return response

    async def get_auto_ml_status(self, start_auto_ml_request: "GetAutoMlStatusRequest") -> "GetAutoMlStatusResponse":
        """Retrieve an available status messages about a specific training session

        Args:
            start_auto_ml_request (GetAutoMlStatusRequest): The Grpc request message

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, if no current AdapterManager is found in the active list

        Returns:
            GetAutoMlStatusResponse: The Grpc response message
        """
        if (start_auto_ml_request.session_id in self.__adapter_managers.keys()):
            return self.__adapter_managers[start_auto_ml_request.session_id].get_auto_ml_status()
        print(f"GET_AUTO_ML_STATUS DID NOT FIND KEY {start_auto_ml_request.session_id} inside {self.__adapter_managers.keys()}")
        raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"get_auto_ml_status: Adapter session {start_auto_ml_request.session_id} does not exist can not get status!")

    async def explain_model(self, explain_auto_ml_request: "ExplainModelRequest") -> "ExplainModelResponse":
        """Request the adapter to perform a probability prediction on a previously ended training session, using the waiting AdapterManager from the training session

        Args:
            explain_auto_ml_request (ExplainModelRequest): The Grpc request message

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, if no current AdapterManager is found in the active list

        Returns:
            ExplainModelResponse: The Grpc response message
        """
        if (explain_auto_ml_request.session_id in self.__adapter_managers.keys()):
            result = await self.__adapter_managers[explain_auto_ml_request.session_id].explain_model(explain_auto_ml_request)
            return result
        raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"explain_model: Adapter session {explain_auto_ml_request.session_id} does not exist can not get model explanation!")

    @inject
    async def predict_model(self, predict_model_request: "PredictModelRequest", adapter_manager: AdapterManager = Provide["managers.adapter_manager"]) -> "PredictModelResponse":
        """Request the adapter to perform a model prediction using a new uploaded live dataset

        Args:
            predict_model_request (PredictModelRequest): The Grpc request message
            adapter_manager (AdapterManager, optional): Injected AdapterManager instance providing the adapter functionality. Defaults to Provide["managers.adapter_manager"].

        Returns:
            PredictModelResponse: The Grpc response message
        """
        result = await adapter_manager.predict_model(predict_model_request)
        del adapter_manager
        return result
