
from enum import auto
from AdapterExplainerDashboardManager import AdapterExplainerDashboardManager
from DataStorage import DataStorage
import json, logging, os, asyncio
from ControllerBGRPC import *

class AdapterRuntimeExplainerDashboardManager:
    """The AdapterRuntimePredictionManager manages the explainer dashboards
    """

    def __init__(self, data_storage: DataStorage, user_id: str, model_id: str, session_id: str) -> None:
        """Initiate a new AdapterRuntimeExplainerDashboardManager instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model_id (str): Unique model record id
            session_id (str): Unique session id
        """
        self.__data_storage: DataStorage = data_storage
        self.__user_id = user_id
        self.__model_id = model_id
        self.__session_id = session_id
        self.__log = logging.getLogger('AdapterRuntimeExplainerDashboardManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__automl_addresses = {
            ":autokeras":       ["AUTOKERAS_SERVICE_HOST", "AUTOKERAS_SERVICE_PORT"],
            ":flaml":           ["FLAML_SERVICE_HOST",     "FLAML_SERVICE_PORT"],
            ":autosklearn":     ["SKLEARN_SERVICE_HOST",   "SKLEARN_SERVICE_PORT"],
            ":autogluon":       ["AUTOGLUON_SERVICE_HOST", "AUTOGLUON_SERVICE_PORT"],
            ":autocve":         ["AUTOCVE_SERVICE_HOST",   "AUTOCVE_SERVICE_PORT"],
            ":autopytorch":     ["PYTORCH_SERVICE_HOST",   "PYTORCH_SERVICE_PORT"],
            ":mljar":           ["MLJAR_SERVICE_HOST",     "MLJAR_SERVICE_PORT"],
            ":alphad3m":        ["ALPHAD3M_SERVICE_HOST",  "ALPHAD3M_SERVICE_PORT"],
            ":mcfly":           ["MCFLY_SERVICE_HOST", 	   "MCFLY_SERVICE_PORT"],
            ":evalml":          ["EVALML_SERVICE_HOST",    "EVALML_SERVICE_PORT"],
            ":pycaret":         ["PYCARET_SERVICE_HOST", "PYCARET_SERVICE_PORT"],
            ":tpot":            ["TPOT_SERVICE_HOST", "TPOT_SERVICE_PORT"],
            ":gama":            ["GAMA_SERVICE_HOST", "GAMA_SERVICE_PORT"],
            ":lama":            ["LAMA_SERVICE_HOST", "LAMA_SERVICE_PORT"],
            ":h2o_automl":      ["H2O_SERVICE_HOST", "H2O_SERVICE_PORT"],
        }
        return

    def start_explainer_dashboard(self, kubernetes_client):

        found, model = self.__data_storage.get_model(self.__user_id, self.__model_id)

        if model.get("dashboard_path", "") == "":
            return #TODO ERROR NO DASHBOARD

        self.__log.debug(f"create_new_prediction: getting adapter endpoint information for automl {model['auto_ml_solution']}")
        host, port = map(os.getenv, self.__automl_addresses[model["auto_ml_solution"].lower()])
        port = int(port)
        self.__log.debug(f"create_new_prediction: creating new prediction adapter manager and adapter manager agent")
        adapter_prediction = AdapterExplainerDashboardManager(model["dashboard_path"], self.__session_id, host, port)
        self.__adapter = adapter_prediction
        result = adapter_prediction.start_explainer_dashboard()

        if os.getenv("KUBERNETES_CLUSTER") == "YES":
            print(f"ADD DASHBOARD PATH: {self.__session_id} URL: {result.url.split(':')[0]}, PORT: {int(result.url.split(':')[1])}")
            kubernetes_client.add_path(f"{self.__session_id}", result.url.split(":")[0], int(result.url.split(":")[1]))
            #For the kubernetes redirection to work properly we need to use double session id
            result.url = "https://" + os.getenv("KUBERNETES_URL") + "/" + self.__session_id + "/" + self.__session_id
        else:
            result.url = "http://" + result.url
        return result

    def stop_explainer_dashboard(self, kubernetes_client):
        if os.getenv("KUBERNETES_CLUSTER") == "YES":
            print(f"REMOVE DASHBOARD PATH: {self.__session_id}")
            kubernetes_client.remove_path(f"{self.__session_id}")
        return self.__adapter.stop_explainer_dashboard()
