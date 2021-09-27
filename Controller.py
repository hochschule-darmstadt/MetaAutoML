from concurrent import futures

import os
import glob
import sys
import string

import grpc
import Controller_pb2
import Controller_pb2_grpc
import Adapter_pb2
import Adapter_pb2_grpc

import logging
import json

from ControllerManager import ControllerManager

def _load_credential_from_file(filepath):
    """
    Load the certificate from disk
    ---
    Parameter
    1. path to certificate to read
    ---
    Return the certificate str
    """
    real_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(real_path, 'rb') as f:
        return f.read()

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DATASET_FOLDER = os.path.join(ROOT_PATH, 'omaml/datasets')

SERVER_CERTIFICATE = _load_credential_from_file('certificate/server.crt')
SERVER_CERTIFICATE_KEY = _load_credential_from_file('certificate/server.key')
#ROOT_CERTIFICATE = _load_credential_from_file('certificate/root.crt')

controllerManager = ControllerManager(DATASET_FOLDER)

class ControllerServiceServicer(Controller_pb2_grpc.ControllerServiceServicer):
    """Missing associated documentation comment in .proto file."""
    
    def __init__(self):
        self = self

    def GetAutoMlModel(self, request, context):
        """Missing associated documentation comment in .proto file."""
        response = controllerManager.GetAutoMlModel(request)
        return response
            
    def GetDatasets(self, request, context):
        """Missing associated documentation comment in .proto file."""
        datasets = controllerManager.GetDatasets()
        return datasets

    def GetDataset(self, request, context):
        """Missing associated documentation comment in .proto file."""
        response = controllerManager.GetDataset(request)
        return response

    def GetSessions(self, request, context):
        response = controllerManager.GetSessions(request)
        return response

    def GetSessionStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        response = controllerManager.GetSessionStatus(request)
        return response


    def GetTabularDatasetColumnNames(self, request, context):
        """Missing associated documentation comment in .proto file."""
        response = controllerManager.GetTabularDatasetColumnNames(request)
        return response

    def GetTasks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        response = controllerManager.GetTasks(request)
        return response

    def UploadDatasetFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        response = controllerManager.UploadNewDataset(request)
        return response

    def StartAutoMLprocess(self, request, context):
        """Missing associated documentation comment in .proto file."""
        response = controllerManager.StartAutoMLProcess(request)
        return response

def serve():
    """
    Boot the gRPC server and wait for incoming connections
    """
    server_credentials = grpc.ssl_server_credentials(((
        SERVER_CERTIFICATE_KEY,
        SERVER_CERTIFICATE,
    ),))
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Controller_pb2_grpc.add_ControllerServiceServicer_to_server(ControllerServiceServicer(), server)
    #server.add_insecure_port('[::]:50051')
    server.add_secure_port('0.0.0.0:5001', server_credentials)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
    print('done.')
    