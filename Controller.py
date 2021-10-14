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

SERVER_CERTIFICATE = _load_credential_from_file('certificate/server.crt')
SERVER_CERTIFICATE_KEY = _load_credential_from_file('certificate/server.key')
#ROOT_CERTIFICATE = _load_credential_from_file('certificate/root.crt')


class ControllerServiceServicer(Controller_pb2_grpc.ControllerServiceServicer):
    """includes all gRPC functions available for the client frontend"""
    
    def __init__(self):
        self = self
        try:
          if os.environ["RUNTIME"]: #Only available in Cluster
            DATASET_FOLDER = os.path.join(ROOT_PATH, 'omaml/datasets')
            self._controllerManager = ControllerManager(DATASET_FOLDER)
        except KeyError: # Raise error if the variable is not set, only for local run
            DATASET_FOLDER = os.path.join(ROOT_PATH, 'omaml/datasets')
            self._controllerManager = ControllerManager(DATASET_FOLDER)
            
    def GetAutoMlModel(self, request, context):
        """ return the generated model as a .zip for one AutoML by its session id."""
        response = self._controllerManager.GetAutoMlModel(request)
        return response
            
    def GetDatasets(self, request, context):
        """return all datasets of a specific type."""
        datasets = self._controllerManager.GetDatasets()
        return datasets

    def GetDataset(self, request, context):
        """return the content of a specific dataset. The result is a collection of TableColumns containing the datatype of a column, its name, and the first entries of the column."""
        response = self._controllerManager.GetDataset(request)
        return response

    def GetSessions(self, request, context):
        """return a list of all sessions the controller has knowledge of. """
        response = self._controllerManager.GetSessions(request)
        return response

    def GetSessionStatus(self, request, context):
        """return the status of a specific session. The result is a session status and a list of the automl output and its status."""
        response = self._controllerManager.GetSessionStatus(request)
        return response


    def GetTabularDatasetColumnNames(self, request, context):
        """return all the column names of a tabular dataset."""
        response = self._controllerManager.GetTabularDatasetColumnNames(request)
        return response

    def GetTasks(self, request, context):
        """return all supported AutoML tasks."""
        response = self._controllerManager.GetTasks(request)
        return response

    def UploadDatasetFile(self, request, context):
        """upload a new dataset file as bytes to the controller repository."""
        response = self._controllerManager.UploadNewDataset(request)
        return response

    def StartAutoMLprocess(self, request, context):
        """start a new AutoML run, using the provided configuration."""
        response = self._controllerManager.StartAutoMLProcess(request)
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
    