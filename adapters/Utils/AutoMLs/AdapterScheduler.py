import uuid
from AdapterManager import *
from AdapterBGRPC import *
from dependency_injector.wiring import inject, Provide

class AdapterScheduler:

    def __init__(self) -> None:
        self.__adapter_managers: dict[str, AdapterManager] = {}
        return 

    @inject
    async def start_auto_ml(self, start_auto_ml_request, adapter_manager: AdapterManager = Provide["managers.adapter_manager"]):
        new_session_id = str(uuid.uuid4())
        self.__adapter_managers[new_session_id] = adapter_manager
        adapter_manager.start_auto_ml(start_auto_ml_request, new_session_id)
        adapter_manager.start()
        response = StartAutoMlResponse()
        response.session_id = new_session_id
        return response
    async def get_auto_ml_status(self, start_auto_ml_request: "GetAutoMlStatusRequest"):
        if (start_auto_ml_request.session_id in self.__adapter_managers.keys()):
            return self.__adapter_managers[start_auto_ml_request.session_id].get_auto_ml_status()
        print(f"GET_AUTO_ML_STATUS DID NOT FIND KEY {start_auto_ml_request.session_id} inside {self.__adapter_managers.keys()}")
        raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"get_auto_ml_status: Adapter session {start_auto_ml_request.session_id} does not exist can not get status!")

    async def explain_model(self, explain_auto_ml_request: "ExplainModelRequest"):
        if (explain_auto_ml_request.session_id in self.__adapter_managers.keys()):
            result = await self.__adapter_managers[explain_auto_ml_request.session_id].explain_model(explain_auto_ml_request)
            return result
        raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"explain_model: Adapter session {explain_auto_ml_request.session_id} does not exist can not get model explanation!")

    @inject
    async def predict_model(self, predict_model_request: "PredictModelRequest", adapter_manager: AdapterManager = Provide["managers.adapter_manager"]):
        result = await adapter_manager.predict_model(predict_model_request)
        del adapter_manager
        return result
