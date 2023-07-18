from dependency_injector.wiring import inject, Provide
from Container import *
from AdapterBGRPC import *
from AdapterScheduler import *

class AdapterService(AdapterServiceBase):
    def __init__(self):
        """
        These variables are used by the ExplainModel function.
        """

    @inject
    async def start_auto_ml(self, start_automl_request: "StartAutoMlRequest",
        adapter_scheduler: AdapterScheduler=Provide[Application.managers.adapter_scheduler]
    ) -> "StartAutoMlResponse":
        return await adapter_scheduler.start_auto_ml(start_automl_request)

    @inject
    async def get_auto_ml_status(self, get_auto_ml_status: "GetAutoMlStatusRequest",
        adapter_scheduler: AdapterScheduler=Provide[Application.managers.adapter_scheduler]
    ) -> "GetAutoMlStatusResponse":
        return await adapter_scheduler.get_auto_ml_status(get_auto_ml_status)

    @inject
    async def explain_model(
        self, explain_model_request: "ExplainModelRequest",
        adapter_scheduler: AdapterScheduler=Provide[Application.managers.adapter_scheduler]
    ) -> "ExplainModelResponse":
        return await adapter_scheduler.explain_model(explain_model_request)

    @inject
    async def create_explainer_dashboard(
        self, create_explainer_dashboard_request: "CreateExplainerDashboardRequest",
        adapter_scheduler: AdapterScheduler=Provide[Application.managers.adapter_scheduler]
    ) -> "CreateExplainerDashboardResponse":
        return await adapter_scheduler.create_explainer_dashboard(create_explainer_dashboard_request)

    @inject
    async def start_explainer_dashboard(
        self, start_explainer_dashboard_request: "StartExplainerDashboardRequest",
        adapter_scheduler: AdapterScheduler=Provide[Application.managers.adapter_scheduler]
    ) -> "StartExplainerDashboardResponse":
        return await adapter_scheduler.start_explainer_dashboard(start_explainer_dashboard_request)

    @inject
    async def stop_explainer_dashboard(
        self, stop_explainer_dashboard_request: "StopExplainerDashboardRequest",
        adapter_scheduler: AdapterScheduler=Provide[Application.managers.adapter_scheduler]
    ) -> "StopExplainerDashboardResponse":
        return await adapter_scheduler.stop_explainer_dashboard(stop_explainer_dashboard_request)

    @inject
    async def predict_model(
        self, predict_model_request: "PredictModelRequest",
        adapter_scheduler: AdapterScheduler=Provide[Application.managers.adapter_scheduler]
    ) -> "PredictModelResponse":
        return await adapter_scheduler.predict_model(predict_model_request)

