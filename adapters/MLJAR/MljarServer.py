import json
import logging
import os
import pickle
import shutil
import time
from concurrent import futures

import grpc
import pandas as pd
from AdapterUtils import *
from JsonUtil import get_config_property
from grpclib.server import Server
from AdapterService import AdapterService
from Container import *




async def main():
    server = Server([AdapterService()])
    await server.start(get_config_property('grpc-server-address'), os.getenv('GRPC_SERVER_PORT'))
    await server.wait_closed()

if __name__ == '__main__':
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    logging.basicConfig()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    #serve()
    print('done.')