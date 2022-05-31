import os
import pandas as pd

import Controller_pb2

from AdapterManager import AdapterManager
from CsvManager import CsvManager
from RdfManager import RdfManager
from persistence import DataStorage, Dataset

class ControllerManager(object):
    """
    Implementation of the controller functionality
    """

    def __init__(self, data_storage: DataStorage):
        """
        Controller Manager init function
        ---
        Parameter
        1. local datasets folder path
        ---
        """
        self.__rdfManager = RdfManager()
        self.__adapterManager = AdapterManager()
        self.__sessions = {}
        self.__sessionCounter = 1
        self.__data_storage = data_storage
        return

    def GetAutoMlModel(self, request) -> Controller_pb2.GetAutoMlModelResponse:
        """
        Get the generated model zip for one AutoML 
        ---
        Parameter
        1. session id
        ---
        Return a .zip containing the model and executable script
        """
        return self.__sessions[request.sessionId].get_automl_model(request)

    def GetCompatibleAUtoMlSolutions(self, request) -> Controller_pb2.GetCompatibleAutoMlSolutionsResponse:
        """
        Get list of comptatible AutoML solutions
        ---
        Parameter
        1. current confiugration
        ---
        Return a list of compatible AutoML
        """
        return self.__rdfManager.GetCompatibleAutoMlSolutions(request)

    def GetDatasets(self):
        """
        Get all datasets for a specific task
        ---
        Parameter
        1. TODO add parameter for session object
        ---
        Return a list of compatible datasets
        """
        response = Controller_pb2.GetDatasetsResponse()

        username = "autml_user"
        all_datasets: list[Dataset] = self.__data_storage.get_datasets(username)
        
        for dataset in all_datasets:
            try:
                rows, cols = pd.read_csv(dataset.path).shape
                response_dataset = Controller_pb2.Dataset()
                response_dataset.fileName = dataset.path
                response_dataset.type = "TABULAR"
                response_dataset.rows = rows
                response_dataset.columns = cols
                response_dataset.creation_date.seconds = int(dataset.mtime)
                response_dataset.creation_date.nanos = int(dataset.mtime % 1 * 1e9)
                response.dataset.append(response_dataset)
            except Exception as e:
                print(f"exception: {e}")
                
        return response

    def GetDataset(self, request) -> Controller_pb2.GetDatasetResponse:
        """
        Get dataset details for a specific dataset
        ---
        Parameter
        1. dataset name
        ---
        Return dataset details
        The result is a list of TableColumns containing:
        name: the name of the dataset
        datatype: the datatype of the column
        firstEntries: the first couple of rows of the dataset
        """
        # TODO WHEN USER MANAGEMENT IS ADDED; CORRECT FILTERING
        username = "autml_user"
        dataset = self.__data_storage.get_dataset(username, request.name)
        dataset = CsvManager.read_dataset(dataset.path)
        return dataset

    def GetSessions(self, request) -> Controller_pb2.GetSessionsResponse:
        """
        Get all sessions
        ---
        Return list of all sessions
        """
        response = Controller_pb2.GetSessionsResponse()
        for i in self.__sessions:
            response.sessionIds.append(self.__sessions[i].get_id())
        return response

    def GetSessionStatus(self, request) -> Controller_pb2.GetSessionStatusResponse:
        """
        Get status of a specific session
        ---
        Parameter
        1. session id
        ---
        Return the session status
        """
        return self.__sessions[request.id].get_session_status()

    def GetTabularDatasetColumnNames(self, request) -> Controller_pb2.GetTabularDatasetColumnNamesResponse:
        """
        Get column names for a specific tabular dataset
        ---
        Parameter
        1. dataset name
        ---
        Return list of column names
        """
        username = "automl_user"
        dataset: Dataset = self.__data_storage.get_dataset(username, request.datasetName)
        columnNames = CsvManager.read_column_names(dataset.path)
        return columnNames
    
    def GetSupportedMlLibraries(self, request) -> Controller_pb2.GetSupportedMlLibrariesResponse:
        """
        Get supported ML libraries for a task
        ---
        Parameter
        1. task identifier
        ---
        Return list of ML libraries
        """
        return self.__rdfManager.GetSupportedMlLibraries(request)

    def GetDatasetCompatibleTasks(self, request) -> Controller_pb2.GetDatasetCompatibleTasksResponse:
        """
        Get compatible tasks for a specific dataset
        ---
        Parameter
        1. dataset name
        ---
        Return list of tasks
        """
        return self.__rdfManager.GetDatasetCompatibleTasks(request)

    def UploadNewDataset(self, dataset: 'dict[str, str]') -> Controller_pb2.UploadDatasetFileResponse:
        """
        Upload a new dataset
        ---
        Parameter
        1. dataset information
        ---
        Return upload status
        """
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # file_dest = os.path.join(script_dir, 'datasets')

        # P: save reference to file in database (eg path)
        #    * actual file should remain on disk
        # "Dataset" in Data Model

        username = "automl_user"
        self.__data_storage.save_dataset(username, dataset.name, dataset.content)
        response = Controller_pb2.UploadDatasetFileResponse()
        response.returnCode = 0
        return response

    def StartAutoMLProcess(self, configuration) -> Controller_pb2.StartAutoMLprocessResponse:
        """
        Start a new AutoML process
        ---
        Parameter
        1. Run configuration
        ---
        Return start process status
        """
        response = Controller_pb2.StartAutoMLprocessResponse()
        newSession = self.__adapterManager.start_automl(configuration, self.__datasetFolder,
                                                               self.__sessionCounter)
        # P: save session details
        #    "Training" in Data Model
        self.__sessions[str(self.__sessionCounter)] = newSession
        self.__sessionCounter += 1
        response.result = 1
        response.sessionId = newSession.get_id()
        return response

    def TestAutoML(self, request) -> Controller_pb2.TestAutoMLResponse:
        """
        Start a new AutoML process as Test
        ---
        Parameter
        1. Run configuration
        ---
        Return start process status
        """ 
        session = self.__sessions.get(request.sessionId)
        automls = session.automls
        test_auto_ml = None
        for automl in automls:
            if automl.name == request.autoMlName:
                test_auto_ml = automl.testSolution(request.testData, request.sessionId)
                break
        if test_auto_ml:
            response = Controller_pb2.TestAutoMLResponse(predictions=test_auto_ml.predictions)
            response.score = test_auto_ml.score
            response.predictiontime = test_auto_ml.predictiontime
        else:
            response = Controller_pb2.TestAutoMLResponse()
        return response
