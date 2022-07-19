import os
import pandas as pd
from requests import request
from AutoMLSession import AutoMLSession
import json

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
        self.__data_storage = data_storage
        self.__rdfManager = RdfManager()
        self.__adapterManager = AdapterManager(self.__data_storage)
        self.__sessions: dict[str, AutoMLSession] = {}
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
            self.__data_storage.save_dataset(username, "titanic_train.csv", dataset, ":tabular", "Titanic")
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
        models = self.__data_storage.get_models(request.username, request.session_id)
        result = GetAutoMlModelResponse()
        result.name = os.path.basename(os.path.normpath(models[0]["path"]))
        with open(models[0]["path"], "rb") as a:
            result.file = a.read()
        return result

    def GetCompatibleAUtoMlSolutions(self, request: "GetCompatibleAutoMlSolutionsRequest") -> "GetCompatibleAutoMlSolutionsResponse":
        """
        Get list of comptatible AutoML solutions
        ---
        Parameter
        1. current configuration
        ---
        Return a list of compatible AutoML
        """
        return self.__rdfManager.GetCompatibleAutoMlSolutions(request)

    def GetDatasetTypes(self, request: "GetDatasetTypesRequest") -> "GetDatasetTypesResponse":
        """
        Get all dataset types
        ---
        Return list of all dataset types
        """
        return self.__rdfManager.GetDatasetTypes(request)

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
                response_dataset = Dataset()
                if dataset['type'] == ':tabular':
                    response_dataset.rows = dataset['analysis']['basic analysis']['number_of_rows']
                    response_dataset.columns = dataset['analysis']['basic analysis']['number_of_columns']
                response_dataset.identifier = str(dataset["_id"])
                response_dataset.file_name = dataset["name"]
                response_dataset.type = dataset['type']
                response_dataset.creation_date = datetime.fromtimestamp(int(dataset["mtime"]))
                response.dataset.append(response_dataset)
            except Exception as e:
                print(f"exception: {e}")
                
        return response

    def GetDatasetTypes(self, request: "GetDatasetTypesRequest") -> "GetDatasetTypesResponse":
        """
        Get all dataset types
        ---
        Return list of all dataset types
        """
        return self.__rdfManager.GetDatasetTypes(request)

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
        all_sessions: list[dict[str, object]] = self.__data_storage.get_sessions(request.username)
        
        for session in all_sessions:
            try:
                response.session_ids.append(str(session["_id"]))
            except Exception as e:
                print(f"exception: {e}")
                
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
        response = GetSessionStatusResponse() 
        session = self.__data_storage.get_session(request.username, request.id)
        if session == None:
            raise Exception(f"cannot find session with id: {request.id}")
        session_models = self.__data_storage.get_models(request.username, request.id)
        
        if len(list(session_models)) == 0:
            return response

        response.status = session["status"]
        for model in list(session_models):
            autoMlStatus = AutoMlStatus()
            autoMlStatus.name = model["automl_name"]
            autoMlStatus.status = model["status"]
            autoMlStatus.messages[:] =  model["status_messages"]
            autoMlStatus.test_score =  model["test_score"]
            autoMlStatus.validation_score =  model["validation_score"]
            autoMlStatus.runtime =  model["runtime"]
            autoMlStatus.predictiontime =  model["prediction_time"]
            autoMlStatus.model =  model["model"]
            autoMlStatus.library =  model["library"]
            response.automls.append(autoMlStatus)
        
        response.dataset_id = session["dataset_id"]
        response.dataset_name = session["dataset_name"]
        response.task = session["task"]
        response.configuration = json.dumps(session["configuration"])
        for automl in session['required_automls']:
            response.required_auto_mls.append(automl)
        response.runtime_constraints = json.dumps(session["runtime_constraints"])
        response.dataset_configuration = json.dumps(session["dataset_configuration"])

        return response
    
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

    def GetDatasetCompatibleTasks(self, request: "GetDatasetCompatibleTasksRequest") -> "GetDatasetCompatibleTasksResponse":
        """
        Get compatible tasks for a specific dataset
        ---
        Parameter
        1. dataset name
        2. dataset type
        ---
        Return list of tasks
        """
        dataset = self.__data_storage.find_dataset(request.username, request.dataset_name)
        return self.__rdfManager.GetDatasetCompatibleTasks(request, dataset[1]["type"])

    def GetObjectsInformation(self, request: "GetObjectsInformationRequest") -> "GetObjectsInformationResponse":
        """
        Get all information for a specific object
        ---
        Parameter
        1. object id
        ---
        Return dictonary of object informations
        """
        print("GET OBJECT INFOS TRIGGERED")
        return self.__rdfManager.GetObjectsInformation(request)

    def UploadNewDataset(self, dataset: "UploadDatasetFileRequest") -> "UploadDatasetFileResponse":
        """
        Upload a new dataset
        ---
        Parameter
        1. dataset information
        ---
        Return upload status
        """
        # NOTE: dataset fields mixed up (bug in dummy)
        #dataset.file_name = dataset.content.decode("utf-8")
        #dataset.content = bytes(dataset.username, "ascii")
        #dataset.username = "User"


        dataset_id: str = self.__data_storage.save_dataset(dataset.username, dataset.file_name, dataset.content, dataset.type, dataset.dataset_name)
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
            "dataset_id": str(dataset["_id"]),
            "dataset_name": dataset["name"],
            "task": configuration.task,
            "configuration": json.loads(configuration.configuration),
            "dataset_configuration": json.loads(configuration.dataset_configuration),
            "runtime_constraints": json.loads(configuration.runtime_constraints),
            "test_configuration": json.loads(configuration.test_configuration),
            "metric": configuration.metric,
            "status": "busy",
            "models": [],
            "required_automls": list(configuration.required_auto_mls),
            "file_configuration": json.loads(configuration.file_configuration)
        }
        sess_id = self.__data_storage.insert_session(configuration.username, config)
        print(f"inserted new session: {sess_id}")

        # will be called when any automl is done
        # NOTE: will run in parallel
        def callback(session_id, model_id, model: 'dict[str, object]'):
            _mdl_id = self.__data_storage.update_model(configuration.username, model_id, model)
            print(f"updated model: {_mdl_id}")
            model_list = self.__data_storage.get_models(configuration.username, session_id)
            # lock data storage to prevent race condition between get and update
            with self.__data_storage.lock():
                # append new model to session
                _sess = self.__data_storage.get_session(configuration.username, session_id)
                if len(_sess["models"]) == len(model_list)-1:
                    self.__data_storage.update_session(configuration.username, session_id, {
                        "models": _sess["models"] + [model_id],
                        "status": "completed"
                    })
                else:
                    self.__data_storage.update_session(configuration.username, session_id, {
                        "models": _sess["models"] + [model_id]
                    })


        newSession: AutoMLSession = self.__adapterManager.start_automl(configuration, dataset_folder,
                                                               sess_id, configuration.username, callback)

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
