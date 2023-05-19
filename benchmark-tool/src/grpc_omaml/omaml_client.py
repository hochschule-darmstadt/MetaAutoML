from grpc_omaml import ControllerServiceStub
from grpclib.client import Channel
from config.config_accessor import get_omaml_server_host, get_omaml_server_port
from ssl import SSLContext, PROTOCOL_TLSv1_2, CERT_NONE
from config.config_accessor import get_disable_certificate_check


class OmamlClient:
    grpc_client: ControllerServiceStub

    def __init__(self):
        # strangely enough, this is the type that the grpc library expects
        ssl: SSLContext | bool = True
        if get_disable_certificate_check():
            ssl = self.__get_ignore_certificate_config()

        channel = Channel(
            host=get_omaml_server_host(),
            port=get_omaml_server_port(),
            ssl=ssl,
        )
        self.grpc_client = ControllerServiceStub(channel=channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # type: ignore
        self.grpc_client.channel.close()

    def __get_ignore_certificate_config(self):
        """Creates a ssl configuration that ignores the certificate.

        Returns:
            ssl configuration
        """
        ssl = SSLContext(PROTOCOL_TLSv1_2)
        ssl.check_hostname = False
        ssl.verify_mode = CERT_NONE
        return ssl
