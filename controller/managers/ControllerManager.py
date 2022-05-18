import os
import pandas as pd

import Controller_pb2

from AdapterManager import AdapterManager
from CsvManager import CsvManager
from RdfManager import RdfManager

class ControllerManager(object):
    """
    Implementation of the controller functionality
    """

    def __init__(self, datasetFolder):
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
        self.__datasetFolder = datasetFolder
        # ensure dataset folder exists
        if not os.path.exists(self.__datasetFolder):
            os.makedirs(self.__datasetFolder)
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
        datasets = Controller_pb2.GetDatasetsResponse()
        # TODO: ADD DATASET MANAGEMENT OVER DATABASE
        with os.scandir(self.__datasetFolder) as dirs:
            for entry in dirs:
                try:
                    rows, cols = pd.read_csv(os.path.join(self.__datasetFolder, entry.name)).shape
                    dataset = Controller_pb2.Dataset()
                    dataset.fileName = entry.name
                    dataset.type = "TABULAR"
                    dataset.rows = rows
                    dataset.columns = cols
                    mtime = os.path.getmtime(os.path.join(self.__datasetFolder, entry.name))
                    dataset.creation_date.seconds = int(mtime)
                    dataset.creation_date.nanos = int(mtime % 1 * 1e9)
                    datasets.dataset.append(dataset)
                except Exception as e:
                    print(e)
        return datasets

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
        dataset = CsvManager.read_dataset(os.path.join(self.__datasetFolder, request.name))
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
        columnNames = CsvManager.read_column_names(os.path.join(self.__datasetFolder, request.datasetName))
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

    def UploadNewDataset(self, dataset) -> Controller_pb2.UploadDatasetFileResponse:
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
        print(f"UploadNewDataset({str(dataset.__dict__)})")
        response = Controller_pb2.UploadDatasetFileResponse()
        response.returnCode = 0
        filename_dest = os.path.join(os.path.normpath(self.__datasetFolder), dataset.name)
        save_file = open(filename_dest, 'wb')
        save_file.write(dataset.content)
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
        print(f"StartAutoMLProcess({str(newSession.__dict__)}")
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
