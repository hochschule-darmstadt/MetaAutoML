import os, signal
import asyncio
from AdapterBGRPC import *
from multiprocessing import Process

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
        import sys, importlib
        importlib.reload(sys.modules['explainerdashboard'])
        from explainerdashboard import ClassifierExplainer, ExplainerDashboard
        if os.getenv("LOCAL_EXECUTION") == "YES" or os.getenv("DOCKER_COMPOSE") == "YES":
            print(self.__path)
            self.__dashboard = ExplainerDashboard(ClassifierExplainer.from_file(self.__path))
        else:
            self.__dashboard = ExplainerDashboard(ClassifierExplainer.from_file(self.__path), url_base_pathname=f"/{self.__session_id}/")
        self.__dashboard.run(self.__port)
            #self.__dashboard.run(self.__port, host=gos.getenv("ADAPTER_NAME"))
        print("thread ended")

    def start_explainer_dashboard(self, request: "StartExplainerDashboardRequest") -> "StartExplainerDashboardResponse":
        self.__path = request.path
        result = StartExplainerDashboardResponse()
        result.result = DashboardCode.DASHBOARD_BOOTED_SUCCESSFULLY
        if os.getenv("LOCAL_EXECUTION") == "YES":
            result.url = f"127.0.0.1:{self.__port}"
        else:
            result.url = f"{os.getenv('ADAPTER_NAME')}:{self.__port}"
        print(f"Booting XAI dashboard {result.url}")
        return result
