import os
import pandas as pd


from Controller_bgrpc import *

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

    def GetAutoMlModel(self, request: "GetAutoMlModelRequest") -> "GetAutoMlModelResponse":
        """
        Get the generated model zip for one AutoML 
        ---
        Parameter
        1. session id
        ---
        Return a .zip containing the model and executable script
        """
        return self.__sessions[request.sessionId].get_automl_model(request)

    def GetCompatibleAUtoMlSolutions(self, request: "GetCompatibleAutoMlSolutionsRequest") -> "GetCompatibleAutoMlSolutionsResponse":
        """
        Get list of comptatible AutoML solutions
        ---
        Parameter
        1. current confiugration
        ---
        Return a list of compatible AutoML
        """
        return self.__rdfManager.GetCompatibleAutoMlSolutions(request)

    def GetDatasets(self, request: "GetDatasetsRequest") -> "GetDatasetsResponse":
        """
        Get all datasets for a specific task
        ---
        Parameter
        1. TODO add parameter for session object
        ---
        Return a list of compatible datasets
        """
        datasets = GetDatasetsResponse()
        # TODO: ADD DATASET MANAGEMENT OVER DATABASE
        with os.scandir(self.__datasetFolder) as dirs:
            for entry in dirs:
                try:
                    rows, cols = pd.read_csv(os.path.join(self.__datasetFolder, entry.name)).shape
                    dataset = Dataset()
                    dataset.file_name = entry.name
                    dataset.type = "TABULAR"
                    dataset.columns = cols
                    dataset.rows = rows
                    mtime = os.path.getmtime(os.path.join(self.__datasetFolder, entry.name))
                    dataset.creation_date = datetime.fromtimestamp(mtime)
                    datasets.dataset.append(dataset)
                except Exception as e:
                    print(e)
        return datasets

    def GetDataset(self, request: "GetDatasetRequest") -> "GetDatasetResponse":
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

    def GetSessions(self, request: "GetSessionsRequest") -> "GetSessionsResponse":
        """
        Get all sessions
        ---
        Return list of all sessions
        """
        response = GetSessionsResponse()
        for i in self.__sessions:
            response.sessionIds.append(self.__sessions[i].get_id())
        return response

    def GetSessionStatus(self, request: "GetSessionStatusRequest") -> "GetSessionStatusResponse":
        """
        Get status of a specific session
        ---
        Parameter
        1. session id
        ---
        Return the session status
        """
        return self.__sessions[request.id].get_session_status()
    
    def GetSupportedMlLibraries(self, request: "GetSupportedMlLibrariesRequest") -> "GetSupportedMlLibrariesResponse":
        """
        Get supported ML libraries for a task
        ---
        Parameter
        1. task identifier
        ---
        Return list of ML libraries
        """
        return self.__rdfManager.GetSupportedMlLibraries(request)

    def GetTabularDatasetColumnNames(self, request: "GetTabularDatasetColumnNamesRequest") -> "GetTabularDatasetColumnNamesResponse":
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

    def GetDatasetCompatibleTasks(self, request: "GetDatasetCompatibleTasksRequest") -> "GetDatasetCompatibleTasksResponse":
        """
        Get compatible tasks for a specific dataset
        ---
        Parameter
        1. dataset name
        ---
        Return list of tasks
        """
        return self.__rdfManager.GetDatasetCompatibleTasks(request)

    def UploadNewDataset(self, dataset: "UploadDatasetFileRequest") -> "UploadDatasetFileResponse":
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
        response = UploadDatasetFileResponse()
        response.returnCode = 0
        filename_dest = os.path.join(os.path.normpath(self.__datasetFolder), dataset.name)
        save_file = open(filename_dest, 'wb')
        save_file.write(dataset.content)
        return response

    def StartAutoMLProcess(self, configuration: "StartAutoMlProcessRequest") -> "StartAutoMlProcessResponse":
        """
        Start a new AutoML process
        ---
        Parameter
        1. Run configuration
        ---
        Return start process status
        """
        response = Controller_pb2.StartAutoMLprocessResponse()
        
        # will be called when any automl is done
        def callback(session_id, automl_name, result):
            print(f"automl is done: {automl_name}, session: {session_id}, result: {result}")

        newSession = self.__adapterManager.start_automl(configuration, self.__datasetFolder,
                                                               self.__sessionCounter, callback)
        self.__sessions[str(self.__sessionCounter)] = newSession
        self.__sessionCounter += 1
        response.result = 1
        response.sessionId = newSession.get_id()
        return response

    def TestAutoML(self, request: "TestAutoMlResponse") -> "TestAutoMlResponse":
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
