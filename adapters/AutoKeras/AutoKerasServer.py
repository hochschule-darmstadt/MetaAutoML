import logging, asyncio
import os
from Container import *
from JsonUtil import get_config_property
from AdapterBGRPC import *
from grpclib.server import Server
from AdapterService import AdapterService

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
