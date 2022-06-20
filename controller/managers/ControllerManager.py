import os
import pandas as pd
from AutoMLSession import AutoMLSession

import Controller_pb2

from AdapterManager import AdapterManager
from CsvManager import CsvManager
from RdfManager import RdfManager
from persistence.data_storage import DataStorage

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

        # TODO: extend gRPC message with username
        username = "automl_user"
        all_datasets: list[dict[str, object]] = self.__data_storage.get_datasets(username)
        
        for dataset in all_datasets:
            try:
                rows, cols = pd.read_csv(dataset["path"]).shape
                response_dataset = Controller_pb2.Dataset()
                response_dataset.fileName = dataset["path"]
                response_dataset.type = "TABULAR"
                response_dataset.rows = rows
                response_dataset.columns = cols
                response_dataset.creation_date.seconds = int(dataset["mtime"])
                response_dataset.creation_date.nanos = int(dataset["mtime"] % 1 * 1e9)
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
        # TODO: extend gRPC message with username
        username = "automl_user"
        # TODO: change gRPC message to dataset id instead of name
        found, dataset = self.__data_storage.find_dataset(username, request.name)
        if not found:
            raise Exception(f"cannot find dataset with name: {request.dataset}")

        dataset = CsvManager.read_dataset(dataset.path)
        return dataset

    def GetSessions(self, request) -> Controller_pb2.GetSessionsResponse:
        """
        Get all sessions
        ---
        Return list of all sessions
        """
        response = Controller_pb2.GetSessionsResponse()

        # only return sessions from this runtime
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

        # TODO: extend gRPC message with username
        username = "automl_user"
        # TODO: change gRPC message to dataset id instead of name
        found, dataset = self.__data_storage.find_dataset(username, request.datasetName)
        if found: 
            return CsvManager.read_column_names(dataset["path"])
        else:
            # no dataset found -> return empty response
            return Controller_pb2.GetTabularDatasetColumnNamesResponse()
    
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

        # TODO: extend gRPC message with username
        username = "automl_user"
        dataset_id: str = self.__data_storage.save_dataset(username, dataset.name, dataset.content)
        print(f"saved new dataset: {dataset_id}")
        
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

        # TODO: extend gRPC message with username 
        username = "automl_user"
        # find requested dataset 
        # TODO: change gRPC message to dataset id instead of name
        found, dataset = self.__data_storage.find_dataset(username, configuration.dataset)
        if not found:
            raise Exception(f"cannot find dataset with name: {configuration.dataset}")
        
        # TODO: rework file access in AutoMLSession
        #       we do not want to make datastore paths public
        dataset_folder = os.path.dirname(dataset["path"])
        dataset_filename = os.path.basename(dataset["path"])

        # overwrite dataset name for further processing
        #   frontend sends dataset name ("titanic_train_1.csv"), 
        #   but datasets on disk are saved as dataset_id ("629e323a9290ff0cf5a5d4a9")
        configuration.dataset = dataset_filename
        
        # restructure configuration into python dictionaries
        config = {
            "dataset": dataset_filename,
            "task": configuration.task,
            "tabular_config": {
                "target": {
                    "target": configuration.tabularConfig.target.target,
                    "type": configuration.tabularConfig.target.type,
                },
                "features": dict(configuration.tabularConfig.features)
            },
            "file_configuration": dict(configuration.fileConfiguration),
            "metric": configuration.metric,
            "status": "running",
            "models": [],
            "runtime_constraints": {
                "runtime_limit": configuration.runtimeConstraints.runtime_limit,
                "max_iter": configuration.runtimeConstraints.max_iter
            },
            "required_automls": list(configuration.requiredAutoMLs),
        }
        sess_id = self.__data_storage.insert_session(username, config)
        print(f"inserted new session: {sess_id}")

        # will be called when any automl is done
        # NOTE: will run in parallel
        def callback(session_id, model: 'dict[str, object]'):
            _mdl_id = self.__data_storage.insert_model(username, model)
            print(f"inserted new model: {_mdl_id}")

            # lock data storage to prevent race condition between get and update
            with self.__data_storage.lock():
                # append new model to session
                _sess = self.__data_storage.get_session(username, session_id)
                self.__data_storage.update_session(username, session_id, {
                    "models": _sess["models"] + [_mdl_id],
                    "status": "completed"
                })


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
