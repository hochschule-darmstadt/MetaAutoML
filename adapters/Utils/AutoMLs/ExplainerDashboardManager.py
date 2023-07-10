import os, signal
import asyncio
from AdapterBGRPC import *
from multiprocessing import Process
from JsonUtil import get_config_property

class ExplainerDashboardManager(Process):
    """The base Explainer Dashboard Manager object providing the shared functionality between all adapters for the explainer dashboard

    Args:
        Thread (Thread): Allowing the ExplainerDashboardManager to start a background thread
    """
    def __init__(self, port, session_id) -> None:
        """Initialize a new ExplainerDashboardManager instance
        """
        self.__port = port
        self.__session_id = session_id
        super().__init__()

    def get_session_id(self):
        return self.__session_id

    def run(self):
        """Start the AutoML solution as a background process
        """

        from explainerdashboard import ClassifierExplainer, ExplainerDashboard
        self.__dashboard = ExplainerDashboard(ClassifierExplainer.from_file(self.__path))
        self.__dashboard
        if get_config_property("local_execution") == "YES":
            self.__dashboard.run(self.__port)
        else:
            self.__dashboard.run(self.__port, host=get_config_property('adapter-name'))
        print("thread ended")

    def start_explainer_dashboard(self, request: "StartExplainerDashboardRequest") -> "StartExplainerDashboardResponse":
        from explainerdashboard import ClassifierExplainer, ExplainerDashboard
        self.__path = request.path
        result = StartExplainerDashboardResponse()
        result.result = DashboardCode.DASHBOARD_BOOTED_SUCCESSFULLY
        if get_config_property("local_execution") == "YES":
            result.url = f"127.0.0.1:{self.__port}"
        else:
            result.url = f"{get_config_property('adapter-name')}:{self.__port}"
        print(f"Booting XAI dashboard {result.url}")
        return result
