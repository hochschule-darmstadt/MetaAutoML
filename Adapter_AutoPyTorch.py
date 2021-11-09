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
    """ AutoML Adapter Service implementation. Service provide functionality to execute and interact with the current AutoML process. """

    def __init__(self):
        self = self

    def StartAutoML(self, request, context):
        """ 
        Execute a new AutoML run. 
        """
        try:
            #saving AutoML configuration JSON
            with open('pytorch-job.json',"w+") as f:
                json.dump(request.processJson, f)
            
            #Start AutoML process
            try:
                #if os.environ["RUNTIME"]: #Only available in Cluster
                process = subprocess.Popen(["python", "AutoML.py", ""], stdout=subprocess.PIPE, universal_newlines=True)
            except KeyError: # Raise error if the variable is not set, only for local run
                # Check os platform
                if sys.platform == "linux" or sys.platform == "linux2":
                    # Pythonpath in Linux systems
                    pypath = "python"
                elif sys.platform == "darwin":
                    # Pythonpath in Mac OS X systems
                    print("Don't know what to do if OS X. Figure out by your own.")
                    return
                elif sys.platform == "win32":
                    # Pythonpath in Windows systems
                    pypath = ".\env\Scripts\python.exe"
                else:
                    print("Error: Could not detect os platform")
                    return
                process = subprocess.Popen([pypath, "AutoML.py", ""], stdout=subprocess.PIPE, universal_newlines=True)
            capture = ""
            s = process.stdout.read(1)
            capture += s
            #Run until no more output is produced by the subprocess
            while len(s) > 0:
                if capture[len(capture)-1] == '\n':
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
            outputJson = {}
            try:
                if os.environ["RUNTIME"]: #Only available in Cluster
                    print("RUNNING DOCKER")
                    if not os.path.exists("omaml/output"): #ensure output folder exists
                        os.makedirs("omaml/output")
                    zip_content_path = os.path.join(BASE_DIR, "templates/output")
                    shutil.make_archive("pytorch-export", 'zip', zip_content_path)
                    shutil.move("pytorch-export.zip","omaml/output/pytorch-export.zip")
                    outputJson = {"file_name": "pytorch-export.zip"}
                    outputJson.update({"file_location": "omaml/output/"})
            except KeyError:  # Raise error if the variable is not set, only for local run
                print("RUNNING LOCAL")
                zip_content_path = os.path.join(BASE_DIR, "Adapter-AutoPyTorch/templates/output")
                shutil.make_archive("pytorch-export", 'zip', zip_content_path)
                outputJson = {"file_name": "pytorch-export.zip"}
                outputJson.update({"file_location": os.path.join(BASE_DIR, "Adapter-AutoPyTorch")})
        
            response = Adapter_pb2.StartAutoMLResponse()
            response.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS
            response.outputJson = json.dumps(outputJson)
            yield response
        except Exception as e:
            print(e.message)
            context.set_details(f"Error while executing AutoPytorch: {e.message}")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return Adapter_pb2.StartAutoMLResponse()

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