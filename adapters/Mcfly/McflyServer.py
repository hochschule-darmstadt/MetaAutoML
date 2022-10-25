import os
import json
import time
import logging
from concurrent import futures

from Container import *
from AdapterUtils import *
from JsonUtil import get_config_property
from grpclib.server import Server
from AdapterService import AdapterService

async def main():
    """The adapter main function starting the adapter GRPC server and waiting on incoming requests of the controller
    """
    server = Server([AdapterService()])
    await server.start(get_config_property('grpc-server-address'), os.getenv('GRPC_SERVER_PORT'))
    await server.wait_closed()

if __name__ == '__main__':
    """Python entry point setting up the dependency injection and starting main
    """
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    logging.basicConfig()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('done.')