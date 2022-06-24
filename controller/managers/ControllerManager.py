import os
import pandas as pd
from requests import request
from AutoMLSession import AutoMLSession

import uuid

from Controller_bgrpc import *

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

    def CreateNewUser(self, request: "CreateNewUserRequest") -> "CreateNewUserResponse":
        """
        Create a new OMA-ML managed user "account"
        ---
        Parameter
        1. empty request object
        ---
        Return a new OMA-ML user id
        """
        username = str(uuid.uuid4())
        if self.__data_storage.CheckIfUserExists(username) == True: #User already exists
            return CreateNewUserResponse(ResultCode.RESULT_CODE_ERROR_CAN_NOT_CREATE_USER, "")
        else:
            dataset = CsvManager.ReadDefaultDatasetAsBytes()
            self.__data_storage.save_dataset(username, "titanic_train.csv", dataset)
            return CreateNewUserResponse(ResultCode.RESULT_CODE_OKAY, username)
            

    def GetAutoMlModel(self, request: "GetAutoMlModelRequest") -> "GetAutoMlModelResponse":
        """
        Get the generated model zip for one AutoML 
        ---
        Parameter
        1. session id
        ---
        Return a .zip containing the model and executable script
        """
        return self.__sessions[request.session_id].get_automl_model(request)

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

    def GetDatasetTypes(self, request: "GetDatasetTypesRequest") -> "GetDatasetTypesResponse":
        #TODO TRAINING WIZZARD
        return

    def GetDatasetType(self, request: "GetDatasetTypeRequest") -> "GetDatasetTypeResponse":
        #TODO TRAINING WIZZARD
        return

    def GetDatasets(self, request: "GetDatasetsRequest") -> "GetDatasetsResponse":
        """
        Get all datasets for a specific task
        ---
        Parameter
        1. TODO add parameter for session object
        ---
        Return a list of compatible datasets
        """
        response = GetDatasetsResponse()
        all_datasets: list[dict[str, object]] = self.__data_storage.get_datasets(request.username)
        
        for dataset in all_datasets:
            try:
                rows, cols = pd.read_csv(dataset["path"]).shape
                response_dataset = Dataset()
                response_dataset.identifier = str(dataset["_id"])
                response_dataset.file_name = dataset["name"]
                response_dataset.type = "TABULAR"
                response_dataset.rows = rows
                response_dataset.columns = cols
                response_dataset.creation_date = datetime.fromtimestamp(int(dataset["mtime"]))
                response.dataset.append(response_dataset)
            except Exception as e:
                print(f"exception: {e}")
                
        return response

    def GetDataset(self, request: "GetDatasetRequest") -> "GetDatasetResponse":
        """
        Get dataset details for a specific dataset
        ---
        Parameter
        1. dataset identifier
        ---
        Return dataset details
        The result is a list of TableColumns containing:
        name: the name of the dataset
        datatype: the datatype of the column
        firstEntries: the first couple of rows of the dataset
        """
        # TODO: change gRPC message to dataset id instead of name
        found, dataset = self.__data_storage.find_dataset(request.username, request.identifier)
        if not found:
            raise Exception(f"cannot find dataset with name: {request.dataset}")

        dataset = CsvManager.read_dataset(dataset["path"])
        return dataset

    def GetSessions(self, request: "GetSessionsRequest") -> "GetSessionsResponse":
        """
        Get all sessions
        ---
        Return list of all sessions
        """
        response = GetSessionsResponse()

        # only return sessions from this runtime
        for id in self.__sessions.keys():
            response.session_ids.append(id)

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

        # TODO: change gRPC message to dataset id instead of name
        found, dataset = self.__data_storage.find_dataset(request.username, request.datasetName)
        if found: 
            return CsvManager.read_column_names(dataset["path"])
        else:
            # no dataset found -> return empty response
            return GetTabularDatasetColumnNamesResponse()
    
    def GetSupportedMlLibraries(self, request) -> GetSupportedMlLibrariesResponse:
        """
        Get supported ML libraries for a task
        ---
        Parameter
        1. task identifier
        ---
        Return list of ML libraries
        """
        return self.__rdfManager.GetSupportedMlLibraries(request)

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
        dataset_id: str = self.__data_storage.save_dataset(dataset.username, dataset.name, dataset.content)
        print(f"saved new dataset: {dataset_id}")
        
        response = UploadDatasetFileResponse()
        response.return_code = 0
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
        response = StartAutoMlProcessResponse()
        # find requested dataset 
        # TODO: change gRPC message to dataset id instead of name
        found, dataset = self.__data_storage.find_dataset(configuration.username, configuration.dataset)
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
                    "target": configuration.tabular_config.target.target,
                    "type": configuration.tabular_config.target.type,
                },
                "features": dict(configuration.tabular_config.features)
            },
            "file_configuration": dict(configuration.file_configuration),
            "metric": configuration.metric,
            "status": "running",
            "models": [],
            "runtime_constraints": {
                "runtime_limit": configuration.runtime_constraints.runtime_limit,
                "max_iter": configuration.runtime_constraints.max_iter
            },
            "required_automls": list(configuration.required_auto_mls),
        }
        sess_id = self.__data_storage.insert_session(configuration.username, config)
        print(f"inserted new session: {sess_id}")

        # will be called when any automl is done
        # NOTE: will run in parallel
        def callback(session_id, model: 'dict[str, object]'):
            _mdl_id = self.__data_storage.insert_model(configuration.username, model)
            print(f"inserted new model: {_mdl_id}")

            # lock data storage to prevent race condition between get and update
            with self.__data_storage.lock():
                # append new model to session
                _sess = self.__data_storage.get_session(configuration.username, session_id)
                self.__data_storage.update_session(configuration.username, session_id, {
                    "models": _sess["models"] + [_mdl_id],
                    "status": "completed"
                })


        newSession: AutoMLSession = self.__adapterManager.start_automl(configuration, dataset_folder,
                                                               sess_id, callback)

        self.__sessions[sess_id] = newSession
        response.result = 1
        response.session_id = newSession.get_id()
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
            response = TestAutoMlResponse(predictions=test_auto_ml.predictions)
            response.score = test_auto_ml.score
            response.predictiontime = test_auto_ml.predictiontime
        else:
            response = TestAutoMlResponse()
        return response
