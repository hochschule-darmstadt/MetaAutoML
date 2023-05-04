from grpc_omaml import ControllerServiceStub
from grpclib.client import Channel
from config.config_accessor import get_omaml_server_host, get_omaml_server_port


def create_omaml_client():
    """Creates a new omaml client.

    Returns:
        ControllerServiceStub: The omaml client
    """
    channel = Channel(host=get_omaml_server_host(), port=get_omaml_server_port())
    return ControllerServiceStub(channel=channel)
