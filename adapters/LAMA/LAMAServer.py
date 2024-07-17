import json
import logging
import os
import shutil
import time, asyncio
from Container import *
from concurrent import futures

import dill
from AdapterUtils import *
from grpclib.server import Server
from AdapterService import AdapterService

async def main():
    """The adapter main function starting the adapter GRPC server and waiting on incoming requests of the controller
    """
    server = Server([AdapterService()])
    await server.start(os.getenv("GRPC_SERVER_ADDRESS"), os.getenv('GRPC_SERVER_PORT'))
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
    #serve()
    print('done.')
