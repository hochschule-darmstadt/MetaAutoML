import os
import pandas as pd
from requests import request
from AutoMLSession import AutoMLSession
import json
from google.protobuf.timestamp_pb2 import Timestamp

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
        self.__trainings: dict[str, AutoMLSession] = {}
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
        ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
        if self.__data_storage.CheckIfUserExists(username) == True: #User already exists
            return CreateNewUserResponse(ResultCode.RESULT_CODE_ERROR_CAN_NOT_CREATE_USER, "")
        else:
            CsvManager.CopyDefaultDataset(username)
            self.__data_storage.InsertDataset(username, "titanic_train.csv", ":tabular", "Titanic")
            return CreateNewUserResponse(ResultCode.RESULT_CODE_OKAY, username)
            

    def GetAutoMlModel(self, request: "GetAutoMlModelRequest") -> "GetAutoMlModelResponse":
        """
        Get the generated model zip for one AutoML 
        ---
        Parameter
        1. training id
        ---
        Return a .zip containing the model and executable script
        """
        models = self.__data_storage.GetModels(request.username, request.training_id)
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
        all_datasets: list[dict[str, object]] = self.__data_storage.GetDatasets(request.username)
        
        for dataset in all_datasets:
            try:
                response_dataset = Dataset()
                
                response_dataset.analysis = json.dumps(dataset['analysis'])
                response_dataset.size = dataset['size']
                response_dataset.identifier = str(dataset["_id"])
                response_dataset.name = dataset["name"]
                response_dataset.type = dataset['type']
                response_dataset.creation_date = datetime.fromtimestamp(int(dataset["mtime"]))
                response_dataset.file_configuration = dataset["file_configuration"]
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
        response = GetDatasetResponse()
        found, dataset = self.__data_storage.GetDataset(request.username, request.identifier)
        
        try:
            response_dataset = Dataset()
            response_dataset.analysis = json.dumps(dataset['analysis'])
            response_dataset.size = dataset['size']
            response_dataset.identifier = str(dataset["_id"])
            response_dataset.name = dataset["name"]
            response_dataset.type = dataset['type']
            response_dataset.creation_date = datetime.fromtimestamp(int(dataset["mtime"]))
            response_dataset.file_name = dataset["file_name"]
            response_dataset.file_configuration = dataset["file_configuration"]
            response.dataset_infos = response_dataset
        except Exception as e:
            print(f"exception: {e}")
                
        return response

    def GetTrainings(self, request: "GetTrainingsRequest") -> "GetTrainingsResponse":
        """
        Get all trainings
        ---
        Return list of all trainings
        """
        response = GetTrainingsResponse()
        all_trainings: list[dict[str, object]] = self.__data_storage.GetTrainings(request.username)
        
        for training in all_trainings:
            try:
                response.training_ids.append(str(training["_id"]))
            except Exception as e:
                print(f"exception: {e}")
                
        return response

    def GetTraining(self, request: "GetTrainingRequest") -> "GetTrainingResponse":
        """
        Get status of a specific Training
        ---
        Parameter
        1. Training id
        ---
        Return the Training status
        """
        response = GetTrainingResponse() 
        training = self.__data_storage.GetTraining(request.username, request.id)
        if training == None:
            raise Exception(f"cannot find training with id: {request.id}")
        training_models = self.__data_storage.GetModels(request.username, request.id)
        
        if len(list(training_models)) == 0:
            return response

        response.status = training["status"]
        for model in list(training_models):
            autoMlStatus = AutoMlStatus()
            autoMlStatus.identifier = str(model["_id"])
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
            response.identifier = str(model["_id"])
            response.dataset_id = model["dataset_id"]
                    
        
        response.dataset_id = training["dataset_id"]
        response.dataset_name = training["dataset_name"]
        response.task = training["task"]
        response.start_time = training["start_time"]
        response.identifier = str(training["_id"])
        response.configuration = json.dumps(training["configuration"])
        for automl in training['required_automls']:
            response.required_auto_mls.append(automl)
        for lib in training['required_libraries']:
            response.required_ml_libraries.append(lib)
        response.runtime_constraints = json.dumps(training["runtime_constraints"])
        response.dataset_configuration = json.dumps(training["dataset_configuration"])

        return response
    
    def GetAllTrainings(self, request: "GetAllTrainingsRequest") -> "GetAllTrainingsResponse":
        """
        Get list of all trainings
        ---
        Parameter
        1. user identifier
        ---
        Return list of All trainings
        """
        response = GetAllTrainingsResponse() 

        all_trainings: list[dict[str, object]] = self.__data_storage.GetTrainings(request.username)
        
        for training in all_trainings:
            try:
                trainingItem = GetTrainingResponse()

                training_models = self.__data_storage.GetModels(request.username, str(training["_id"]))

                trainingItem.status = training["status"]
                for model in list(training_models):
                    autoMlStatus = AutoMlStatus()
                    autoMlStatus.identifier = str(model["_id"])
                    autoMlStatus.name = model["automl_name"]
                    autoMlStatus.status = model["status"]
                    autoMlStatus.messages[:] =  model["status_messages"]
                    autoMlStatus.test_score =  model["test_score"]
                    autoMlStatus.validation_score =  model["validation_score"]
                    autoMlStatus.runtime =  model["runtime"]
                    autoMlStatus.predictiontime =  model["prediction_time"]
                    autoMlStatus.model =  model["model"]
                    autoMlStatus.library =  model["library"]
                    trainingItem.automls.append(autoMlStatus)
                    trainingItem.identifier = str(model["_id"])
                    trainingItem.dataset_id = model["dataset_id"]

                trainingItem.dataset_id = training["dataset_id"]
                trainingItem.dataset_name = training["dataset_name"]
                trainingItem.task = training["task"]
                trainingItem.configuration = json.dumps(training["configuration"])
                trainingItem.start_time = training["start_time"]
                trainingItem.identifier = str(training["_id"])
                for automl in training['required_automls']:
                    trainingItem.required_auto_mls.append(automl)
                for lib in training['required_libraries']:
                    trainingItem.required_ml_libraries.append(lib)
                trainingItem.runtime_constraints = json.dumps(training["runtime_constraints"])
                trainingItem.dataset_configuration = json.dumps(training["dataset_configuration"])
                response.trainings.append(trainingItem)
            except Exception as e:
                print(f"exception: {e}")


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

    def GetTabularDatasetColumn(self, request: "GetTabularDatasetColumnRequest") -> "GetTabularDatasetColumnResponse":
        """
        Get column names for a specific tabular dataset
        ---
        Parameter
        1. dataset name
        ---
        Return list of column names
        """
        found, dataset = self.__data_storage.GetDataset(request.username, request.dataset_identifier)
        if found: 
            return CsvManager.GetColumns(dataset["path"])
        else:
            # no dataset found -> return empty response
            return GetTabularDatasetColumnResponse()

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
        dataset = self.__data_storage.GetDataset(request.username, request.dataset_name)
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

    def GetHomeOverviewInformation(self, request: "GetHomeOverviewInformationRequest") -> "GetHomeOverviewInformationResponse":
        """
        Get all information for the home information page
        ---
        Parameter
        1. user id
        ---
        Return home information to display
        """
        response = GetHomeOverviewInformationResponse()
        response.dataset_amount = len(self.__data_storage.GetDatasets(request.user))
        response.model_amount = len(self.__data_storage.GetModels(request.user))
        response.training_amount = len(self.__data_storage.GetTrainings(request.user))
        response.running_training_amount = len([t for t in self.__data_storage.GetTrainings(request.user) if t["status"] == "busy"])
        return response


    def GetModels(self, request: "GetModelsRequest") -> "GetModelsResponse":
        """
        Get all models, or optinally get top 3 models for a dataset
        ---
        Parameter
        1. request object
        ---
        Return dictonary of object informations
        """
        response = GetModelsResponse()
        top3Counter = 0
        def GetScore(e):
            return e["test_score"]
        
        model_list = self.__data_storage.GetModels(request.username, dataset_id=request.dataset_id)
        model_list.sort(key=GetScore, reverse=True)
        
        for model in list(model_list):
            if  top3Counter >= 3 and request.top3 == True:
                return response
            model_info = ModelInformation()
            model_info.identifier = str(model["_id"])
            model_info.automl = model["automl_name"]
            model_info.status = model["status"]
            model_info.status_messages[:] =  model["status_messages"]
            model_info.test_score =  model["test_score"]
            model_info.validation_score =  model["validation_score"]
            model_info.runtime =  model["runtime"]
            model_info.prediction_time =  model["prediction_time"]
            model_info.model =  model["model"]
            model_info.library =  model["library"]
            model_info.training_id = model["training_id"]
            model_info.dataset_id = model["dataset_id"]
            response.models.append(model_info)
            top3Counter = top3Counter + 1
            
        return response

    def GetModel(self, request: "GetModelRequest") -> "GetModelResponse":
        """
        Get all models, or optinally get top 3 models for a dataset
        ---
        Parameter
        1. request object
        ---
        Return dictonary of object informations
        """
        response = GetModelResponse()
        
        model = self.__data_storage.GetModel(request.username, request.model_id)
        
        model_info = ModelInformation()
        model_info.identifier = str(model["_id"])
        model_info.automl = model["automl_name"]
        model_info.status = model["status"]
        model_info.status_messages[:] =  model["status_messages"]
        model_info.test_score =  model["test_score"]
        model_info.validation_score =  model["validation_score"]
        model_info.runtime =  model["runtime"]
        model_info.prediction_time =  model["prediction_time"]
        model_info.model =  model["model"]
        model_info.library =  model["library"]
        model_info.training_id = model["training_id"]
        model_info.dataset_id = model["dataset_id"]
        response.model = model_info
            
        return response


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


        dataset_id: str = self.__data_storage.InsertDataset(dataset.username, dataset.file_name, dataset.type, dataset.dataset_name)
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
        found, dataset = self.__data_storage.GetDataset(configuration.username, configuration.dataset)
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
            "required_libraries": list(configuration.required_libraries),
            "file_configuration": json.loads(configuration.file_configuration),
            "start_time": datetime.now()
        }
        training_id = self.__data_storage.InsertTraining(configuration.username, config)
        print(f"inserted new training: {training_id}")

        # will be called when any automl is done
        # NOTE: will run in parallel
        def callback(training_id, model_id, model: 'dict[str, object]'):
            # lock data storage to prevent race condition between get and update
            with self.__data_storage.Lock():
                # append new model to training
                training = self.__data_storage.GetTraining(configuration.username, training_id)
                model["dataset_id"] = training["dataset_id"]
                _mdl_id = self.__data_storage.UpdateModel(configuration.username, model_id, model)
                model_list = self.__data_storage.GetModels(configuration.username, training_id)
                if len(training["models"]) == len(model_list)-1:
                    self.__data_storage.UpdateTraining(configuration.username, training_id, {
                        "models": training["models"] + [model_id],
                        "status": "completed",
                        "end_time": datetime.now()
                    })
                else:
                    self.__data_storage.UpdateTraining(configuration.username, training_id, {
                        "models": training["models"] + [model_id]
                    })


        newTraining: AutoMLSession = self.__adapterManager.start_automl(configuration, str(dataset["_id"]), dataset_folder,
                                                               training_id, configuration.username, callback)

        self.__trainings[training_id] = newTraining
        response.result = 1
        response.training_id = newTraining.get_id()
        return response

    def TestAutoML(self, request: "TestAutoMlRequest") -> "TestAutoMlResponse":
        """
        Start a new AutoML process as Test
        ---
        Parameter
        1. Run configuration
        ---
        Return start process status
        """ 
        model = self.__data_storage.GetModel(request.username, request.model_id)
        training = self.__data_storage.GetTraining(request.username, model["training_id"])

        config = {
            "task": training["task"],
            "configuration": training["configuration"],
            "dataset_configuration": training["dataset_configuration"],
            "runtime_constraints": training["runtime_constraints"],
            "test_configuration": training["test_configuration"],
            "metric": training["metric"],
            "file_configuration": training["file_configuration"]
        }
        automl = AdapterManager(self.__data_storage)
        test_auto_ml = automl.TestAutoml(request, model["automl_name"], model["training_id"], config)
        if test_auto_ml:
            response = TestAutoMlResponse()
            for prediction in test_auto_ml.predictions:
                response.predictions.append(prediction)
            response.score = test_auto_ml.score
            response.predictiontime = test_auto_ml.predictiontime
        else:
            response = TestAutoMlResponse()
        return response

    def SetDatasetConfiguration(self, request: "SetDatasetConfigurationRequest") -> "SetDatasetConfigurationResponse":
        """
        Persist new dataset configuration in db
        ---
        Parameter
        1. dataset configuration
        ---
        Return 
        """ 
        self.__data_storage.UpdateDataset(request.username, request.identifier, { "file_configuration": request.file_configuration })
        return SetDatasetConfigurationResponse()
