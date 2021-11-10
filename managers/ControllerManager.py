import os
import Controller_pb2
import Controller_pb2_grpc

from StructuredDataManager import StructuredDataManager
from AutoMLSession import AutoMLSession
from CsvManager import CsvManager
from RdfManager import RdfManager


class ControllerManager(object):
    """description of class"""

    def __init__(self, datasetFolder):
        self.__rdfManager = RdfManager()
        self.__structuredDataManager = StructuredDataManager()
        self.__sessions = {}
        self.__sessionCounter = 1
        self.__datasetFolder = datasetFolder
        # ensure dataset folder exists
        if not os.path.exists(self.__datasetFolder):
            os.makedirs(self.__datasetFolder)
        return

    def GetAutoMlModel(self, request) -> Controller_pb2.GetAutoMlModelResponse:
        return self.__sessions[request.sessionId].GetAutoMlModel(request)

    def GetCompatibleAUtoMlSolutions(self, request) -> Controller_pb2.GetCompatibleAutoMlSolutionsResponse:
        return self.__rdfManager.GetCompatibleAutoMlSolutions(request)

    def GetDatasets(self):
        datasets = Controller_pb2.GetDatasetsResponse()
        # TODO: ADD DATASET MANAGEMENT OVER DATABASE
        with os.scandir(self.__datasetFolder) as dirs:
            for entry in dirs:
                dataset = Controller_pb2.Dataset()
                dataset.fileName = entry.name
                dataset.type = "TABULAR"
                datasets.dataset.append(dataset)
        return datasets

    def GetDataset(self, request) -> Controller_pb2.GetDatasetResponse:
        # TODO WHEN USER MANAGEMENT IS ADDED; CORRECT FILTERING
        dataset = CsvManager.ReadDataset(os.path.join(self.__datasetFolder, request.name))
        return dataset

    def GetSessions(self, request) -> Controller_pb2.GetSessionsResponse:
        response = Controller_pb2.GetSessionsResponse()
        for i in self.__sessions:
            response.sessionIds.append(self.__sessions[i].GetId())
        return response

    def GetSessionStatus(self, request) -> Controller_pb2.GetSessionStatusResponse:
        return self.__sessions[request.id].GetSessionStatus()

    def GetTabularDatasetColumnNames(self, request) -> Controller_pb2.GetTabularDatasetColumnNamesResponse:
        columnNames = CsvManager.ReadColumnNames(os.path.join(self.__datasetFolder, request.datasetName))
        return columnNames
    
    def GetSupportedMlLibraries(self, request) -> Controller_pb2.GetSupportedMlLibrariesResponse:
        return self.__rdfManager.GetSupportedMlLibraries(request)

    def GetDatasetCompatibleTasks(self, request) -> Controller_pb2.GetDatasetCompatibleTasksResponse:
        return self.__rdfManager.GetDatasetCompatibleTasks(request)

    def UploadNewDataset(self, dataset) -> Controller_pb2.UploadDatasetFileResponse:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # file_dest = os.path.join(script_dir, 'datasets')
        response = Controller_pb2.UploadDatasetFileResponse()
        response.returnCode = 0
        filename_dest = os.path.join(os.path.normpath(self.__datasetFolder), dataset.name)
        save_file = open(filename_dest, 'wb')
        save_file.write(dataset.content)
        return response

    def StartAutoMLProcess(self, configuration) -> Controller_pb2.StartAutoMLprocessResponse:
        response = Controller_pb2.StartAutoMLprocessResponse()
        newSession = self.__structuredDataManager.start_automl(configuration, self.__datasetFolder,
                                                               self.__sessionCounter)
        self.__sessions[str(self.__sessionCounter)] = newSession
        self.__sessionCounter += 1
        response.result = 1
        response.sessionId = newSession.GetId()
        return response
