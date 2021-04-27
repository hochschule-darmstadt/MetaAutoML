
import glob
import sys
sys.path.append('Rpc/gen-py')

from automl import HelloWorldService
from automl.ttypes import HelloWorldStruct

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class HelloWorldServiceHandler:
    def __init__(self):
        self.log = {}
        
    def HelloWorld(self, input):
        print(input.text)


    
if __name__ == '__main__':
    handler = HelloWorldServiceHandler()
    processor = HelloWorldService.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    
    print('Starting the server...')
    server.serve()
    print('done.')