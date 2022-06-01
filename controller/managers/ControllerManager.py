import os
import pandas as pd
from AutoMLSession import AutoMLSession

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
        self.__sessions: dict[str, AutoMLSession] = {}
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

        username = "automl_user"
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
        username = "automl_user"
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

        # NOTE: should we return all known sessions, or only the ones from this runtime?
                # username = "automl_user"
                # all_sessions = self.__data_storage.get_sessions(username)
                # response.sessionIds = [sess["_id"] for sess in all_sessions]
        for id in self.__sessions.keys():
            response.sessionIds.append(id)

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

    def StartAutoMLProcess(self, configuration: Controller_pb2.StartAutoMLprocessRequest) -> Controller_pb2.StartAutoMLprocessResponse:
        """
        Start a new AutoML process
        ---
        Parameter
        1. Run configuration
        ---
        Return start process status
        """
        response = Controller_pb2.StartAutoMLprocessResponse()

        # restructure configuration into python dictionaries
        config = {
            "dataset": configuration.dataset,
            "task": configuration.task,
            "tabularConfig": {
                "target": {
                    "target": configuration.tabularConfig.target.target,
                    "type": configuration.tabularConfig.target.type,
                },
                "features": dict(configuration.tabularConfig.features)
            },
            "fileConfiguration": dict(configuration.fileConfiguration),
            "metric": configuration.metric,
            "status": "running",
            "models": []
            # TODO: does not work yet:
            # "runtimeConstraints": dict(configuration.runtimeConstraints),
            # "requiredAutomls": dict(configuration.requiredAutoMLs),
        }
        username = "automl_user"
        sess_id = self.__data_storage.insert_session(username, config)

        # will be called when any automl is done
        def callback(session_id, model_details):
            # TODO: mark session as successful/completed
            _mdl_id = self.__data_storage.insert_model(username, model_details)

            # TODO: race condition between get and update, lock db access
            # append new model to session
            _sess = self.__data_storage.get_session(username, session_id)
            self.__data_storage.update_session(username, session_id, {
                "models": _sess["models"] + [_mdl_id] 
            })

        # TODO: rework file access in AutoMLSession
        #       we do not want to make datastore paths public
        dataset: Dataset = self.__data_storage.get_dataset(username, configuration.dataset)
        dataset_folder = os.path.dirname(dataset.path)

        newSession: AutoMLSession = self.__adapterManager.start_automl(configuration, dataset_folder,
                                                               sess_id, callback)

        self.__sessions[sess_id] = newSession
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
