import os, signal
import asyncio
from AdapterBGRPC import *
import threading
import glob
import json
import time
from waitress import serve
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

from explainerdashboard import ClassifierExplainer, ExplainerDashboard, RegressionExplainer
class ExplainerDashboardManager:
    """The base Explainer Dashboard Manager object providing the shared functionality between all adapters for the explainer dashboard

    Args:
        Thread (Thread): Allowing the ExplainerDashboardManager to start a background thread
    """
    def __init__(self, port, session_id) -> None:
        """Initialize a new ExplainerDashboardManager instance
        """
        self.__port = port
        self.__session_id = session_id
        self.__dashboard = None
        self.__stop_event = threading.Event()
        self.__executor = ThreadPoolExecutor(max_workers=1)

    def get_session_id(self):
        return self.__session_id

    # def run(self):
    #     """Start the AutoML solution as a background process
    #     """
    #     from explainerdashboard import ClassifierExplainer, ExplainerDashboard
    #     import sys, importlib
    #     importlib.reload(sys.modules['explainerdashboard'])
    #     from explainerdashboard import ClassifierExplainer, ExplainerDashboard
    #     if os.getenv("LOCAL_EXECUTION") == "YES" or os.getenv("DOCKER_COMPOSE") == "YES":
    #         print(self.__path)
    #         self.__dashboard = ExplainerDashboard(ClassifierExplainer.from_file(self.__path))
    #     else:
    #         self.__dashboard = ExplainerDashboard(ClassifierExplainer.from_file(self.__path), url_base_pathname=f"/{self.__session_id}/")
    #     self.__dashboard.run(self.__port, debug=True, waittress=True)
    #         #self.__dashboard.run(self.__port, host=gos.getenv("ADAPTER_NAME"))
    #     print("thread ended")

    def start_explainer_dashboard(self, request: "StartExplainerDashboardRequest") -> "StartExplainerDashboardResponse":
        self.__path = request.path
        result = StartExplainerDashboardResponse()
        result.result = DashboardCode.DASHBOARD_BOOTED_SUCCESSFULLY
        training_config_files = glob.glob(os.path.join(self.__path, "..", "job", "*-job.json"))
        if training_config_files:
            training_config_file = training_config_files[0]  # Assuming there is only one such file
            with open(training_config_file, 'r') as file:
                training_config = json.load(file)
        if training_config["configuration"]["task"] == ":tabular_classification":
            explainer = ClassifierExplainer.from_file(os.path.join(self.__path, "dashboard.joblib"))
        else:
            explainer = RegressionExplainer.from_file(os.path.join(self.__path, "dashboard.joblib"))
        print("##########################################")
        if os.getenv("LOCAL_EXECUTION") == "YES" or os.getenv("DOCKER_COMPOSE") == "YES":
            print("LOCAL OR DOCKER EXECUTION")
            self.__dashboard = ExplainerDashboard(explainer)
            # self.__dashboard = ExplainerDashboard.from_config(os.path.join(self.__path, "dashboard.yaml"), explainerfile=os.path.join(self.__path, "dashboard.joblib"))
            # self.__dashboard = ExplainerDashboard(ClassifierExplainer.from_file(self.__path))
            result.url = f"{os.getenv('DOCKER_OR_DEBUG_XAI_DASHBOARD_IP')}:{self.__port}"
        else:
            print("CLUSTER EXECUTION: SESSION ID")
            print(f"/{self.__session_id}/")
            self.__dashboard = ExplainerDashboard(explainer, url_base_pathname=f"/{self.__session_id}/")
            # self.__dashboard = ExplainerDashboard.from_config(os.path.join(self.__path, "dashboard.yaml"), explainerfile=os.path.join(self.__path, "dashboard.joblib"), url_base_pathname=f"/{self.__session_id}/")
            # self.__dashboard
            # self.__dashboard = ExplainerDashboard(ClassifierExplainer.from_file(self.__path), url_base_pathname=f"/{self.__session_id}/")
            result.url = f"{os.getenv('ADAPTER_NAME')}:{self.__port}"
        #self.__thread = threading.Thread(target=self.run_dashboard)

        # self.__thread = threading.Thread(target=self.run_dashboard, daemon=True)
        #self.__thread.start()
        loop = asyncio.get_running_loop()
        self._dashboard_future = loop.run_in_executor(
            self.__executor,
            self.run_dashboard
        )
        # self.dashboard_process = multiprocessing.Process(target=self.run_dashboard, args=())
        # self.dashboard_process.start()
        time.sleep(4)  # Give it some time to start
        print(f"Booting XAI dashboard {result.url}")
        return result

    def run_dashboard(self):
        self.__dashboard.run(port=self.__port, debug=True, use_waitress=True)


    def stop_explainer_dashboard(self):
        #self.__thread.join()
        if self._dashboard_future:
            self.__executor.shutdown(wait=False, cancel_futures=True)
        # self.dashboard_process.terminate()
        # self.dashboard_process.join()

