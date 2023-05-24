import multiprocessing
from JsonUtil import get_config_property
from concurrent.futures.process import ProcessPoolExecutor
from grpclib.server import Server
from ssl import SSLContext
import ssl, asyncio, logging, os
from ControllerBGRPC import *
from ControllerServiceManager import ControllerServiceManager
from Container import Application
import nest_asyncio
from grpclib.config import Configuration

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


def _load_credential_from_file(filepath: str) -> bytes:
    """Load the certificate file from disk

    Args:
        filepath (str): Path to the certificate file

    Returns:
        bytes: byte array of certificate file content
    """
    real_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(real_path, 'rb') as f:
        return f.read()

def create_secure_context() -> SSLContext:
    """Create the required SSL context for inbound GRPC connections

    Returns:
        SSLContext: SSL Context for inbound connections
    """
    #Credit: https://github.com/vmagamedov/grpclib/blob/master/examples/mtls/server.py
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_cert_chain(str("certificate/server.crt"), str('certificate/server.key'))
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20')
    ctx.set_alpn_protocols(['h2'])
    """try:
        ctx.set_npn_protocols(['h2'])
    except NotImplementedError:
        pass"""
    return ctx



SERVER_CERTIFICATE = _load_credential_from_file('certificate/server.crt')
SERVER_CERTIFICATE_KEY = _load_credential_from_file('certificate/server.key')


async def main():
    """The controller main function starting the controller GRPC server and waiting on incoming requests of the frontend
    """
    #with ProcessPoolExecutor(max_workers=40) as executor:
    config = Configuration(
        http2_connection_window_size= 2000 * 1024 * 1024,  # 1 MiB
        http2_stream_window_size= 2000 * 1024 * 1024,  # 1 MiB
    )
    server = Server([ControllerServiceManager()], config=config)
    context = SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(certfile="certificate/server.crt", keyfile='certificate/server.key')
    await server.start(get_config_property('controller-server-adress'), get_config_property('controller-server-port'), ssl=create_secure_context())
    await server.wait_closed()


if __name__ == '__main__':
    """Python entry point setting up the dependency injection and starting main
    """
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    loop = asyncio.get_event_loop()
    nest_asyncio.apply()
    loop.run_until_complete(main())
    #Uncomment to activate local logging
    #logging.basicConfig()
    __log = logging.getLogger('ControllerServer')
    __log.setLevel(logging.getLevelName(logging.DEBUG))
    __log.debug("__name__: controller started")
    __log.debug("__name__: controller exited")
