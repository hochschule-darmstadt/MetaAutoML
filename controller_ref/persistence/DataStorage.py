import os, shutil, logging
import threading 
from MongoDbClient import MongoDbClient
from sklearn.model_selection import train_test_split
from sktime.datasets import write_dataframe_to_tsfile
from sktime.datasets import load_from_tsfile_to_dataframe
import pandas as pd
from bson.objectid import ObjectId
from DataSetAnalysisManager import DataSetAnalysisManager
from ControllerBGRPC import *

class DataStorage:
    """
    Centralized Access to File System and Database
    """
    def __init__(self, data_storage_dir: str, storage_lock: threading.Lock, mongo_db_url: str = None):
        """
        Initialize new instance. This should be done already.
        Do _not_ use multiple instances of this class.

        Will connect to the MongoDB database defined in docker-compose
        unless `database` is provided.

        >>> data_storage = DataStorage("/tmp/")

        ----
        Parameter
        1. storage directory on disk
        2. multiprocessing lock for thread safety 
        3. optional Database object (used for Testing)
        """
        self.__log = logging.getLogger('DataStorage')
        self.__log.setLevel(logging.getLevelName(os.getenv("PERSISTENCE_LOGGING_LEVEL")))
        # ensure folder exists
        os.makedirs(data_storage_dir, exist_ok=True)
        self.__storage_dir = data_storage_dir
        self.__mongo: MongoDbClient = MongoDbClient(mongo_db_url)
        self.__lock = storage_lock

    ####################################
    ## MISC DATASTORAGE OPERATIONS
    ####################################
#region

    def check_if_user_exists(self, user_identifier: bool):
        """
        Check if user exists by checking if his database exists
        ---
        >>> id: str = ds.check_if_user_exists("automl_user")
        ---
        Parameter
        1. user identifier
        ---
        Returns database existance status, TRUE == EXITS
        """
        return self.__mongo.check_if_user_exists(user_identifier)

    def lock(self):
        self.__log.debug("lock: aquiring lock...")
        self.__lock.acquire()

    def unlock(self):
        self.__log.debug("unlock: releasing lock...")
        self.__lock.release()

#endregion

    ####################################
    ## DATASET RELATED OPERATIONS
    ####################################
#region 


    def create_dataset(self, user_identifier: str, file_name: str, type: str, name: str) -> str:
        """
        Store dataset contents on disk and insert entry to database.
        ---
        Parameter
        1. user identifier
        2. file name: file name of dataset
        3. type: dataset type
        4. name: dataset name
        ---
        Returns dataset id
        """

        if type == ":image":
            self.__log.debug(f"create_dataset: dataset type is image, removing .zip ending from {name} as not necessary after unzipping anymore...")
            name = name.replace(".zip", "")

        # build dictionary for database
        database_content = {
            "name": name,
            "type": type,
            "analysis": "",
            "models": [],
            "path": "",
            "size": "",
            "mtime": "",
            "file_name" : "",
            "file_configuration": ""
        }

        self.__log.debug("create_dataset: inserting new dataset into database...")
        dataset_id = self.__mongo.insert_dataset(user_identifier, database_content)
        self.__log.debug(f"create_dataset: new dataset inserted with id: {dataset_id}")


        upload_file = os.path.join(self.__storage_dir, user_identifier, "uploads", file_name)
        self.__log.debug(f"create_dataset: upload location is: {upload_file}")
        
        filename_dest = os.path.join(self.__storage_dir, user_identifier, dataset_id, file_name)
        self.__log.debug(f"create_dataset: final persistence location is: {filename_dest}")

        #if os.getenv("MONGO_DB_DEBUG") != "YES":
            # When not in a debug environment (for example within docker) we do not want to add the app section,
            # as this leads to broken links
            #upload_file = upload_file.replace("/app/", "")
            #filename_dest = filename_dest.replace("/app/", "")

        self.__log.debug(f"create_dataset: creating dataset folder location: {filename_dest}")
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
        self.__log.debug(f"create_dataset: moving dataset from: {upload_file} to: {filename_dest}")
        shutil.move(upload_file, filename_dest)
        file_configuration = ""

        if type == ":image":
            self.__log.debug("create_dataset: dataset is of image type: unzipping, deleting zip archive and remove .zip suffix...")
            shutil.unpack_archive(filename_dest, os.path.join(self.__storage_dir, user_identifier, dataset_id))
            os.remove(filename_dest)
            filename_dest = filename_dest.replace(".zip", "")
            fileName = file_name.replace(".zip", "")

        if type == ":tabular" or type == ":text" or type == ":time_series":
            #generate preview of tabular and text dataset
            #previewDf = pd.read_csv(filename_dest)
            #previewDf.head(50).to_csv(filename_dest.replace(".csv", "_preview.csv"), index=False)
            #causes error with different delimiters use normal string division
            self.__log.debug("create_dataset: dataset is of CSV type: creating subset preview file, and generating csv file configuration...")
            with open(filename_dest, encoding="utf8") as file:
                lines = file.readlines()
            with open(filename_dest.replace(".csv", "_preview.csv"), "x") as preview:
                preview_line = lines[:51]
                for line in preview_line:
                    preview.write(line)
                    # preview.write("\n")
            file_configuration = '{"use_header":true, "start_row":1, "delimiter":"comma", "escape_character":"\\\\", "decimal_character":"."}'

        if type == ":time_series_longitudinal":
            self.__log.debug("create_dataset: dataset is of TS nature: creating subset preview file, and generating csv file configuration...")
            TARGET_COL = "target"
            FIRST_N_ROW = 50
            FIRST_N_ITEMS = 3
            SEED = 42
            df_dict = {}

            df_preview = load_from_tsfile_to_dataframe(filename_dest, return_separate_X_and_y=False)
            df_preview = df_preview.rename(columns={"class_vals": TARGET_COL})

            index_preview, _ = train_test_split(
                df_preview.index,
                train_size=min(len(df_preview), FIRST_N_ROW),
                random_state=SEED,
                shuffle=True,
                stratify=df_preview[TARGET_COL]
            )

            df_preview = df_preview.loc[index_preview]

            for col in df_preview.columns:
                # Create a new dictionary key if it doesn't exist
                if col not in df_dict.keys():
                    df_dict[col] = []
                # Extract target values
                if (col == TARGET_COL):
                    for item in df_preview[col]:
                        df_dict[col].append(item)
                else:
                    # Extract the first 3 values from each row and
                    # create a string value, e.g. "[1.9612, 0.9619, 1.0172, ...]"
                    for item in df_preview[col]:
                        preview = item.to_list()
                        preview = preview[0:FIRST_N_ITEMS]
                        preview = str(preview)
                        preview = preview.replace("]", ", ...]")
                        df_dict[col].append(preview)

            # Save the new dataframe as a csv file
            df_preview_filename = filename_dest.replace(".ts", "_preview.csv")
            pd.DataFrame(df_dict).to_csv(df_preview_filename, index=False)
            file_configuration = '{"use_header":true, "start_row":1, "delimiter":"comma", "escape_character":"\\\\", "decimal_character":"."}'

        def get_size(start_path='.'):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)

            return total_size

        self.__log.debug("create_dataset: get the total occupied disc size of the dataset...")
        nbytes = get_size(os.path.join(self.__storage_dir, user_identifier, dataset_id))
        self.__log.debug(f"create_dataset: dataset disc usage is: {nbytes} bytes")

        analysis_result = {}
        # If the dataset is a certain type the dataset can be analyzed.
        if type in [":tabular", ":text", ":time_series", ":time_series_longitudinal"]:
            self.__log.debug("create_dataset: executing dataset analysis...")
            analysis_result = DataSetAnalysisManager({"path": filename_dest,
                                                      "file_configuration": file_configuration,
                                                      "type": type}).analysis()

        success = self.__mongo.update_dataset(user_identifier, dataset_id, {
            "path": filename_dest,
            "size": nbytes,
            "mtime": os.path.getmtime(filename_dest),
            "analysis": analysis_result,
            "file_name": file_name,
            "file_configuration": file_configuration
        })
        assert success, f"cannot update dataset with id {dataset_id}"

        return dataset_id

    def update_dataset(self, user_identifier: str, dataset_identifier: str, new_values: 'dict[str, object]', run_analysis: bool) -> bool:
        """
        Update single dataset with new values. 
        ---
        >>> success: bool = data_storage.UpdateDataset("automl_user", dataset_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. user identifier: name of the user
        2. dataset identifier
        3. new values: dict with new values
        4. run analysis: if the dataset analysis should be executed
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        self.__log.debug(f"update_dataset: updating: {dataset_identifier} for user {user_identifier}, new values {new_values}")
        if run_analysis == True:
            found, dataset = self.get_dataset(user_identifier, dataset_identifier)
            if found is not None:
                self.__log.debug(f"update_dataset: executing dataset analysis for dataset: {dataset_identifier} for user {user_identifier}")
                # If the dataset is a tabular dataset it can be analyzed.
                if dataset['type'] in [":tabular", ":text", ":time_series", ":time_series_longitudinal"]:
                    # Delete old references
                    new_values["analysis"] = ""
                    self.__log.debug(f"update_dataset: deleting old dataset analysis for dataset: {dataset_identifier} for user {user_identifier}")
                    self.__mongo.update_dataset(user_identifier, dataset_identifier, new_values)
                    self.__log.debug(f"update_dataset: saving new dataset analysis for dataset: {dataset_identifier} for user {user_identifier}, new values {new_values}")
                    new_values["analysis"] = DataSetAnalysisManager(dataset).analysis()
                else:
                    self.__log.warn(f"update_dataset: dataset type {dataset['type']} does not support dataset analysis in dataset {dataset_identifier} for user {user_identifier}")
            else:
                self.__log.error(f"update_dataset: executing dataset analysis failed for dataset: {dataset_identifier} for user {user_identifier}, dataset not found")
                raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {dataset_identifier} for user {user_identifier} does not exist, can not execute dataset analysis!")
        return self.__mongo.update_dataset(user_identifier, dataset_identifier, new_values)

    def get_dataset(self, user_identifier: str, dataset_identifier: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the first dataset with this identifier 
        ---
        >>> found, dataset = ds.get_dataset("automl_user", "12323asdas")
        >>> if not found:
                print("We have a problem")

        ---
        Parameter
        1. user identifier 
        2. dataset identifier
        ---
        Returns either `(True, Dataset)` or `(False, None)`.
        """
        result = self.__mongo.get_dataset(user_identifier, {
            "_id": ObjectId(dataset_identifier)
        })

        return result is not None, result

    def get_datasets(self, user_identifier: str) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user. 
        ---
        >>> for dataset in data_storage.GetDatasets("automl_user"):
                print(dataset["path"])

        ---
        Parameter
        1. user_identifier: name of the user
        ---
        Returns `list` of all datasets.
        """
        return [ds for ds in self.__mongo.get_datasets(user_identifier)]

    def delete_dataset(self, user_identifier: str, dataset_identifier: str):
        """
        Delete a dataset and its associated items
        ---
        Parameter
        1. user identifier
        2. dataset identifier
        ---
        Returns amount of deleted objects
        """
        #First check if dataset isn't already deleted
        found, dataset = self.get_dataset(user_identifier, dataset_identifier)
        if not found:
            self.__log.error(f"delete_dataset: attempting to delete a dataset that does not exist: {dataset_identifier} for user {user_identifier}")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {dataset_identifier} does not exist, already deleted?")
        path = dataset["path"]
        path = path.replace("\\"+ dataset["file_name"], "")
        #Before deleting the dataset, delete all related documents
        existing_trainings = self.get_trainings(user_identifier, dataset_identifier)
        self.__log.debug(f"delete_dataset: deleting {existing_trainings.count} trainings")
        for training in existing_trainings:
            try:
                self.delete_training(user_identifier, str(training["_id"]))
            except:
                self.__log.debug(f"delete_dataset: deleting training failed, already deleted. Skipping...")
        self.__mongo.delete_training(user_identifier, { "dataset_id": dataset_identifier})
        self.__log.debug(f"delete_dataset: deleting files within path: {path}")
        shutil.rmtree(path)
        amount_deleted_datasets_result = self.__mongo.delete_dataset(user_identifier, { "dataset_id": dataset_identifier})
        self.__log.debug(f"delete_dataset: documents deleted within dataset: {amount_deleted_datasets_result}")
        return amount_deleted_datasets_result


#endregion

    ####################################
    ## MODEL RELATED OPERATIONS
    ####################################
#region


    def create_model(self, user_identifier: str, model_details: 'dict[str, object]') -> str:
        """
        Insert single model into the database.
        ---
        >>> mdl_id: str = data_storage.create_model("automl_user", {
                "automl_name": "MLJAR",
                "training_id": training_id,
                ...
            })

        ---
        Parameter
        1. user identifier
        2. model details
        ---
        Returns id of new model.
        """
        return self.__mongo.insert_model(user_identifier, model_details)

    def update_model(self, user_identifier: str, model_identifier: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single model with new values. 
        ---
        >>> success: bool = data_storage.update_model("automl_user", model_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. user identifier
        2. model identifier
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.update_model(user_identifier, model_identifier, new_values)

    def get_model(self, user_identifier: str, model_identifier: str = None) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the first model with this identifier 
        ---
        >>> found, model = ds.get_model("automl_user", "asdasd123213")
        >>> if not found:
                print("We have a problem")
        
        ---
        Parameter
        1. user identifier
        2. model identifier
        ---
        Returns either `(True, Model)` or `(False, None)`.
        """
        result = self.__mongo.get_model(user_identifier, {
            "_id": ObjectId(model_identifier)
        })

        return result is not None, result

    def get_models(self, user_identifier: str, training_identifier: str = None, dataset_identifier: str = None) -> 'list[dict[str, object]]':
        """
        Get all models, or all models by training id or dataset id
        ---
        >>> models = ds.GetModels("automl_user", "training_id")

        ---
        Parameter
        1. user identifier
        2. optinally training identifier
        2. optinally dataset identifier
        ---
        Returns a models list
        """
        if training_identifier is not None:
            filter = { "training_id": training_identifier }
        elif dataset_identifier is not None:
            filter = { "dataset_id": dataset_identifier }
        else:
            filter = {}
        result = self.__mongo.get_models(user_identifier, filter)

        return [ds for ds in result]

    def delete_model(self, user_identifier: bool, model_identifier: str):
        """
        Delete model and its associated items
        ---
        Parameter
        1. user identifier
        2. model identifier
        ---
        Returns amount of deleted objects
        """
        #First check if training isn't already deleted
        found, model = self.get_model(user_identifier, model_identifier)
        if not found:
            self.__log.error(f"delete_model: attempting to delete a model that does not exist: {model_identifier} for user {user_identifier}")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {model_identifier} does not exist, already deleted?")
        #Before deleting the model, delete all related documents
        path: str = model["path"]
        if model["automl_name"] == ":alphad3m":
            path = path.replace("\\export\\alphad3m-export.zip", "")
        elif model["automl_name"] == ":autocve":
            path = path.replace("\\export\\autocve-export.zip", "")
        elif model["automl_name"] == ":autogluon":
            path = path.replace("\\export\\gluon-export.zip", "")
        elif model["automl_name"] == ":autokeras":
            path = path.replace("\\export\\keras-export.zip", "")
        elif model["automl_name"] == ":autopytorch":
            path = path.replace("\\export\\pytorch-export.zip", "")
        elif model["automl_name"] == ":autosklearn":
            path = path.replace("\\export\\sklearn-export.zip", "")
        elif model["automl_name"] == ":flaml":
            path = path.replace("\\export\\flaml-export.zip", "")
        elif model["automl_name"] == ":mcfly":
            path = path.replace("\\export\\mcfly-export.zip", "")
        elif model["automl_name"] == ":mljar":
            path = path.replace("\\export\\mljar-export.zip", "")
        try:
            self.__log.debug(f"delete_model: deleting files within path: {path}")
            shutil.rmtree(path)
        except:
            self.__log.error(f"delete_model: deleting files within path: {path} failed, path does not exist")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {model_identifier} file path does not exist, already deleted?")


        amount_deleted_models_result = self.__mongo.delete_model(user_identifier, { "_id": ObjectId(model_identifier) })
        self.__log.debug(f"delete_model: documents deleted within model: {amount_deleted_models_result}")
        return amount_deleted_models_result

#endregion

    ####################################
    ## TRAINING RELATED OPERATIONS
    ####################################
#region

    def create_training(self, user_identifier: str, training_details: 'dict[str, object]') -> str:
        """
        Insert single training into the database.
        ---
        >>> id: str = ds.create_training("automl_user", {
                "dataset": ...,
                ...
            })

        ---
        Parameter
        1. user identifier
        2. training details: training dict to be inserted
        ---
        Returns training id
        """
        return self.__mongo.insert_training(user_identifier, training_details)

    def update_training(self, user_identifier: str, training_identifier: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single training with new values. 
        ---
        >>> success: bool = data_storage.update_training("automl_user", sess_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. user identifier
        2. training identifier
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.update_training(user_identifier, training_identifier, new_values)

    def get_training(self, user_identifier: str, training_identifier: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the first training with this identifier 
        ---
        >>> found, dataset = ds.get_training("automl_user", "asdasd123213")
        >>> if not found:
                print("We have a problem")
        
        ---
        Parameter
        1. user identifier
        2. training identifier
        ---
        Returns either `(True, Training)` or `(False, None)`.
        """
        result = self.__mongo.get_training(user_identifier, {
            "_id": ObjectId(training_identifier)
        })

        return result is not None, result

    def get_trainings(self, user_identifier: str, dataset_identifier:str=None) -> 'list[dict[str, object]]':
        """
        Get all trainings for a user. 
        ---
        >>> for sess in data_storage.get_trainings("automl_user"):
                print(sess["dataset"])

        ---
        Parameter
        1. user identifier
        2. optinally dataset identifier
        ---
        Returns trainings as `list` of dictionaries.
        """
        if dataset_identifier is None:
            return [sess for sess in self.__mongo.get_trainings(user_identifier)]
        else:
            return [sess for sess in self.__mongo.get_trainings(user_identifier, {"dataset_id": dataset_identifier})]
        
    def delete_training(self, user_identifier: bool, training_identifier: str):
        """
        Delete a training and its associated items
        ---
        Parameter
        1. user identifier
        2. training identifier
        ---
        Returns amount of deleted objects
        """
        #First check if training isn't already deleted
        found, training = self.get_training(user_identifier, training_identifier)
        if not found:
            self.__log.error(f"delete_training: attempting to delete a training that does not exist: {training_identifier} for user {user_identifier}")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Training {training_identifier} does not exist, already deleted?")

        #Before deleting the training, delete all related documents
        existing_models = self.get_models(user_identifier, training_identifier=training_identifier)
        self.__log.debug(f"delete_training: deleting {existing_models.count} models")
        for model in existing_models:
            try:
                self.delete_model(user_identifier, str(model["_id"]))
            except:
                self.__log.debug(f"delete_training: deleting model failed, already deleted. Skipping...")
        #Finally delete training
        amount_deleted_trainings_result = self.__mongo.delete_training(user_identifier, { "_id": ObjectId(training_identifier) })
        self.__log.debug(f"delete_training: documents deleted within training: {amount_deleted_trainings_result}")
        return amount_deleted_trainings_result
   
#endregion