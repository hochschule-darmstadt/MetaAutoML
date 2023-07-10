
from ControllerBGRPC import *
import json, logging, os,datetime
from threading import *
import asyncio
from grpclib.client import Channel
from AdapterBGRPC import *
from DataStorage import DataStorage
from AdapterBGRPC import *

class AdapterExplainerDashboardManager:
    """The AdapterExplainerDashboardManager provides functionality for the prediction process to connect to the correct adapter and execute the prediction

    Args:
        Thread (_type_): _description_
    """

    def __init__(self, dashboard_path: str, session_id: str, host: str, port: int) -> None:
        """Initialize a new AdapterExplainerDashboardManager instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            dashboard_path (str): The path to the dashboard files within the adapter
            host (str): The ip address to the AutoML adapter GRPC Server
            port (int): The port to the AutoML adapter GRPC Server
        """
        super(AdapterExplainerDashboardManager, self).__init__()
        self.__log = logging.getLogger('AdapterExplainerDashboardManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__dashboard_path = dashboard_path
        self.__session_id = session_id
        self.__host = host
        self.__port = port

    def start_explainer_dashboard(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        channel = Channel(host=self.__host, port=self.__port)
        service = AdapterServiceStub(channel=channel)
        request = StartExplainerDashboardRequest()
        request.path = self.__dashboard_path
        request.session_id = self.__session_id
        response = loop.run_until_complete(service.start_explainer_dashboard(request))
        channel.close()
        return response

    def stop_explainer_dashboard(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        channel = Channel(host=self.__host, port=self.__port)
        service = AdapterServiceStub(channel=channel)
        request = StopExplainerDashboardRequest()
        request.session_id = self.__session_id
        response = loop.run_until_complete(service.stop_explainer_dashboard(request))
        channel.close()
        return response
