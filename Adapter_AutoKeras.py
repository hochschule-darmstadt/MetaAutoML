import grpc
import os
import sys
import logging
import shutil
import numpy as np
import pandas as pd
import subprocess
import json

import Adapter_pb2
import Adapter_pb2_grpc

from concurrent import futures
from TemplateGenerator import TemplateGenerator

class AdapterServiceServicer(Adapter_pb2_grpc.AdapterServiceServicer):
    """Missing associated documentation comment in .proto file."""

    def __init__(self):
        self = self

    def StartAutoML(self, request, context):
        """Missing associated documentation comment in .proto file."""
        #print(request.dataset_path)
        
        with open('keras-job.json',"w+") as f:
            json.dump(request.processJson, f)

        process = subprocess.Popen([".\env\Scripts\python.exe", "AutoML.py", "TESTETSTA"], stdout=subprocess.PIPE, universal_newlines=True)
        capture = ""
        s = process.stdout.read(1)
        capture += s
        while len(s) > 0:
            if capture[len(capture)-1] is '\n':
                processUpdate = Adapter_pb2.StartAutoMLResponse()
                processUpdate.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_STATUS_UPDATE
                processUpdate.statusUpdate = capture
                processUpdate.outputJson = ""
                yield processUpdate
                sys.stdout.write(capture)
                sys.stdout.flush()
                capture = ""
            capture += s
            s = process.stdout.read(1)
        #Generate python script
        generator = TemplateGenerator()
        generator.GenerateScript()

        #Zip content
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        zip_content_path = os.path.join(BASE_DIR, "Adapter-AutoKeras\\templates\\output")
        
        shutil.make_archive("keras-export", 'zip', zip_content_path)
       
        response = Adapter_pb2.StartAutoMLResponse()
        response.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS
        outputJson = {"file_name": "keras-export.zip"} 
        outputJson.update({"file_location": os.path.join(BASE_DIR, "Adapter-AutoKeras")})
        response.outputJson = json.dumps(outputJson)
        yield response

def serve():
    """
    Boot the gRPC server and wait for incoming connections
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Adapter_pb2_grpc.add_AdapterServiceServicer_to_server(AdapterServiceServicer(), server)
    server.add_insecure_port('0.0.0.0:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
    print('done.')