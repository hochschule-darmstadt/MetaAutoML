import os, shutil, logging
from MongoDbClient import MongoDbClient
from sklearn.model_selection import train_test_split
from sktime.datasets import load_from_tsfile_to_dataframe
import pandas as pd
from bson.objectid import ObjectId
from ControllerBGRPC import *
from threading import Lock



class DataStorage:
    """
    Centralized Access to File System and Database
    """
    def __init__(self, data_storage_dir: str, mongo_db: MongoDbClient = None):
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
        #self.__mongo_db_url = mongo_db_url
        self.__mongo: MongoDbClient = mongo_db
        self.__lock = Lock()

    ####################################
    ## MISC DATASTORAGE OPERATIONS
    ####################################
#region

    def check_if_user_exists(self, user_id: bool):
    #@inject
    #def check_if_user_exists(self, user_id: bool, mongo_db_client: MongoDbClient):
        """
        Check if user exists by checking if his database exists
        ---
        >>> id: str = ds.check_if_user_exists("automl_user")
        ---
        Parameter
        1. user id
        ---
        Returns database existance status, TRUE == EXITS
        """
        return self.__mongo.check_if_user_exists(user_id)
        #return mongo_db_client.check_if_user_exists(user_id)



    def lock(self):
        """
        Lock access to the data storage to a single thread.
        ---
        >>> with data_store.lock():
                # critical region
                sess = data_storage.get_session(...)
                data_storage.update_session(..., {
                    "models": sess["models"] + [new_model]
                })
        """
        return DataStorage.__DbLock(self.__lock)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_DataStorage__mongo']
        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__mongo: MongoDbClient = MongoDbClient(self.__mongo_db_url)

#endregion

    ####################################
    ## DATASET RELATED OPERATIONS
    ####################################
#region 


    def create_dataset(self, user_id: str, file_name: str, type: str, name: str) -> str:
        """
        Store dataset contents on disk and insert entry to database.
        ---
        Parameter
        1. user id
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
            "path": "",
            "file_configuration": {},
            "training_ids": [],
            "analysis": {
                "creation_date": 0,
                "size_bytes": 0
            },
            "is_deleted": False
        }

        self.__log.debug("create_dataset: inserting new dataset into database...")
        dataset_id = self.__mongo.insert_dataset(user_id, database_content)
        self.__log.debug(f"create_dataset: new dataset inserted with id: {dataset_id}")


        upload_file = os.path.join(self.__storage_dir, user_id, "uploads", file_name)
        self.__log.debug(f"create_dataset: upload location is: {upload_file}")
        
        filename_dest = os.path.join(self.__storage_dir, user_id, dataset_id, file_name)
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
        file_configuration = {}

        if type == ":image":
            self.__log.debug("create_dataset: dataset is of image type: unzipping, deleting zip archive and remove .zip suffix...")
            shutil.unpack_archive(filename_dest, os.path.join(self.__storage_dir, user_id, dataset_id))
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
            file_configuration = {"use_header": True, "start_row":1, "delimiter":"comma", "escape_character":"\\", "decimal_character":"."}

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
            file_configuration = {"use_header": True, "start_row":1, "delimiter":"comma", "escape_character":"\\", "decimal_character":"."}

        success = self.__mongo.update_dataset(user_id, dataset_id, {
            "path": filename_dest,
            "file_configuration": file_configuration
        })
        assert success, f"cannot update dataset with id {dataset_id}"

        return dataset_id
        
        
    def update_dataset(self, user_id: str, dataset_id: str, new_values: 'dict[str, object]') -> bool:
        """Update single dataset with new values
        >>> success: bool = data_storage.update_dataset("automl_user", dataset_id, {
                "status": "completed"
            })
        Args:
            user_id (str): user identifier, stored inside the frontend application database
            dataset_id (str): identifier of dataset that will be updated
            new_values (dict[str, object]): dictonary of values that will be update for the dataset
            run_analysis (bool): if the dataset analysis module will be executed for the dataset again

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the dataset to be updated is not present within MongoDB

        Returns:
            bool: if the dataset was updated successfully
        """
        self.__log.debug(f"update_dataset: updating: {dataset_id} for user {user_id}, new values {new_values}")
        return self.__mongo.update_dataset(user_id, dataset_id, new_values)

    def get_dataset(self, user_id: str, dataset_id: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the first dataset with this id 
        ---
        >>> found, dataset = ds.get_dataset("automl_user", "12323asdas")
        >>> if not found:
                print("We have a problem")

        ---
        Parameter
        1. user id 
        2. dataset id
        ---
        Returns either `(True, Dataset)` or `(False, None)`.
        """
        result = self.__mongo.get_dataset(user_id, {
            "_id": ObjectId(dataset_id)
        })

        return result is not None, result

    #def get_datasets(self, user_id: bool):
    def get_datasets(self, user_id: str) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user. 
        ---
        >>> for dataset in data_storage.GetDatasets("automl_user"):
                print(dataset["path"])

        ---
        Parameter
        1. user_id: name of the user
        ---
        Returns `list` of all datasets.
        """
        return [ds for ds in self.__mongo.get_datasets(user_id)]

    def delete_dataset(self, user_id: str, dataset_id: str):
        """
        Delete a dataset and its associated items
        ---
        Parameter
        1. user id
        2. dataset id
        ---
        Returns amount of deleted objects
        """
        #First check if dataset isn't already deleted
        found, dataset = self.get_dataset(user_id, dataset_id)
        if not found:
            self.__log.error(f"delete_dataset: attempting to delete a dataset that does not exist: {dataset_id} for user {user_id}")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {dataset_id} does not exist, already deleted?")
        path = dataset["path"]
        if os.getenv("WIN_DEV_MACHINE") == "YES":
            path = path.replace( "\\"+ os.path.basename(dataset["path"]), "")
        else:
            path = path.replace( "/"+ os.path.basename(dataset["path"]), "")
        #Before deleting the dataset, delete all related documents
        existing_trainings = self.get_trainings(user_id, dataset_id)
        self.__log.debug(f"delete_dataset: deleting {existing_trainings.count} trainings")
        for training in existing_trainings:
            try:
                self.delete_training(user_id, str(training["_id"]))
            except:
                self.__log.debug(f"delete_dataset: deleting training failed, already deleted. Skipping...")
        self.__log.debug(f"delete_dataset: deleting files within path: {path}")
        shutil.rmtree(path)
        amount_deleted_datasets_result = self.__mongo.delete_dataset(user_id, { "_id": ObjectId(dataset_id)})
        self.__log.debug(f"delete_dataset: documents deleted within dataset: {amount_deleted_datasets_result}")
        return amount_deleted_datasets_result


#endregion

    ####################################
    ## MODEL RELATED OPERATIONS
    ####################################
#region


    def create_model(self, user_id: str, model_details: 'dict[str, object]') -> str:
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
        1. user id
        2. model details
        ---
        Returns id of new model.
        """
        return self.__mongo.insert_model(user_id, model_details)

    def update_model(self, user_id: str, model_id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single model with new values. 
        ---
        >>> success: bool = data_storage.update_model("automl_user", model_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. user id
        2. model id
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.update_model(user_id, model_id, new_values)

    def get_model(self, user_id: str, model_id: str = None) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the first model with this id 
        ---
        >>> found, model = ds.get_model("automl_user", "asdasd123213")
        >>> if not found:
                print("We have a problem")
        
        ---
        Parameter
        1. user id
        2. model id
        ---
        Returns either `(True, Model)` or `(False, None)`.
        """
        result = self.__mongo.get_model(user_id, {
            "_id": ObjectId(model_id)
        })

        return result is not None, result

    def get_models(self, user_id: str, training_id: str = None, dataset_id: str = None) -> 'list[dict[str, object]]':
        """
        Get all models, or all models by training id or dataset id
        ---
        >>> models = ds.GetModels("automl_user", "training_id")

        ---
        Parameter
        1. user id
        2. optinally training id
        2. optinally dataset id
        ---
        Returns a models list
        """
        if training_id is not None:
            filter = { "training_id": training_id }
        elif dataset_id is not None:
            found, dataset = self.get_dataset(user_id, dataset_id)
            filter = { "training_id": { '$in': dataset["training_ids"] } }
        else:
            filter = {}
        result = self.__mongo.get_models(user_id, filter)

        return [ds for ds in result]

    def delete_model(self, user_id: bool, model_id: str):
        """
        Delete model and its associated items
        ---
        Parameter
        1. user id
        2. model id
        ---
        Returns amount of deleted objects
        """
        #First check if training isn't already deleted
        found, model = self.get_model(user_id, model_id)
        if not found:
            self.__log.error(f"delete_model: attempting to delete a model that does not exist: {model_id} for user {user_id}")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {model_id} does not exist, already deleted?")
        #Before deleting the model, delete all related documents
        path: str = model["path"]
        if model["auto_ml_solution"] == ":alphad3m":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\alphad3m-export.zip", "")
            else:
                path = path.replace("/export/alphad3m-export.zip", "")
            
        elif model["auto_ml_solution"] == ":autocve":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\autocve-export.zip", "")
            else:
                path = path.replace("/export/autocve-export.zip", "")

        elif model["auto_ml_solution"] == ":autogluon":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\gluon-export.zip", "")
            else:
                path = path.replace("/export/gluon-export.zip", "")

        elif model["auto_ml_solution"] == ":autokeras":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\keras-export.zip", "")
            else:
                path = path.replace("/export/keras-export.zip", "")

        elif model["auto_ml_solution"] == ":autopytorch":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\pytorch-export.zip", "")
            else:
                path = path.replace("/export/pytorch-export.zip", "")

        elif model["auto_ml_solution"] == ":autosklearn":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\sklearn-export.zip", "")
            else:
                path = path.replace("/export/sklearn-export.zip", "")

        elif model["auto_ml_solution"] == ":flaml":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\flaml-export.zip", "")
            else:
                path = path.replace("/export/flaml-export.zip", "")

        elif model["auto_ml_solution"] == ":mcfly":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\mcfly-export.zip", "")
            else:
                path = path.replace("/export/mcfly-export.zip", "")

        elif model["auto_ml_solution"] == ":mljar":
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace("\\export\\mljar-export.zip", "")
            else:
                path = path.replace("/export/mljar-export.zip", "")

        try:
            self.__log.debug("delete_model: deleting predictions")
            for prediction_id in model["prediction_ids"]:
                self.delete_prediction(user_id, prediction_id)
            self.__log.debug(f"delete_model: deleting files within path: {path}")
            shutil.rmtree(path)
        except:
            self.__log.error(f"delete_model: deleting files within path: {path} failed, path does not exist")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {model_id} file path does not exist, already deleted?")


        amount_deleted_models_result = self.__mongo.delete_model(user_id, { "_id": ObjectId(model_id) })
        self.__log.debug(f"delete_model: documents deleted within model: {amount_deleted_models_result}")
        return amount_deleted_models_result

#endregion

    ####################################
    ## TRAINING RELATED OPERATIONS
    ####################################
#region

    def create_training(self, user_id: str, training_details: 'dict[str, object]') -> str:
        """
        Insert single training into the database.
        ---
        >>> id: str = ds.create_training("automl_user", {
                "dataset": ...,
                ...
            })

        ---
        Parameter
        1. user id
        2. training details: training dict to be inserted
        ---
        Returns training id
        """
        return self.__mongo.insert_training(user_id, training_details)

    def update_training(self, user_id: str, training_id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single training with new values. 
        ---
        >>> success: bool = data_storage.update_training("automl_user", sess_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. user id
        2. training id
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.update_training(user_id, training_id, new_values)

    def get_training(self, user_id: str, training_id: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the first training with this id 
        ---
        >>> found, dataset = ds.get_training("automl_user", "asdasd123213")
        >>> if not found:
                print("We have a problem")
        
        ---
        Parameter
        1. user id
        2. training id
        ---
        Returns either `(True, Training)` or `(False, None)`.
        """
        result = self.__mongo.get_training(user_id, {
            "_id": ObjectId(training_id)
        })

        return result is not None, result

    def get_trainings(self, user_id: str, dataset_id:str=None) -> 'list[dict[str, object]]':
        """
        Get all trainings for a user. 
        ---
        >>> for sess in data_storage.get_trainings("automl_user"):
                print(sess["dataset"])

        ---
        Parameter
        1. user id
        2. optinally dataset id
        ---
        Returns trainings as `list` of dictionaries.
        """
        if dataset_id is None:
            return [sess for sess in self.__mongo.get_trainings(user_id)]
        else:
            return [sess for sess in self.__mongo.get_trainings(user_id, {"dataset_id": dataset_id})]
        
    def delete_training(self, user_id: bool, training_id: str):
        """
        Delete a training and its associated items
        ---
        Parameter
        1. user id
        2. training id
        ---
        Returns amount of deleted objects
        """
        #First check if training isn't already deleted
        found, training = self.get_training(user_id, training_id)
        if not found:
            self.__log.error(f"delete_training: attempting to delete a training that does not exist: {training_id} for user {user_id}")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Training {training_id} does not exist, already deleted?")

        #Before deleting the training, delete all related documents
        existing_models = self.get_models(user_id, training_id=training_id)
        self.__log.debug(f"delete_training: deleting {existing_models.count} models")
        for model in existing_models:
            try:
                self.delete_model(user_id, str(model["_id"]))
            except:
                self.__log.debug(f"delete_training: deleting model failed, already deleted. Skipping...")
        #Finally delete training
        amount_deleted_trainings_result = self.__mongo.delete_training(user_id, { "_id": ObjectId(training_id) })
        self.__log.debug(f"delete_training: documents deleted within training: {amount_deleted_trainings_result}")
        return amount_deleted_trainings_result
   
#endregion

    ####################################
    ## PREDICTION RELATED OPERATIONS
    ####################################
#region 

    def create_prediction(self, user_id: str, live_dataset_file_name: str, prediction_details: 'dict[str, object]') -> str:
        """
        Store dataset contents on disk and insert entry to database.
        ---
        Parameter
        1. user id
        2. file name: file name of dataset
        3. type: dataset type
        4. name: dataset name
        ---
        Returns dataset id
        """
        self.__log.debug(f"create_prediction: getting model {prediction_details['model_id']} for new prediction")
        found, model = self.get_model(user_id, prediction_details["model_id"])

        if not found:
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {prediction_details['model_id']} for user {user_id} does not exist, can not create a new prediction!")

        self.__log.debug(f"create_prediction: getting training {model['training_id']} for model")
        found, training = self.get_training(user_id, model["training_id"])
        if not found:
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Training {model['training_id']} for user {user_id} does not exist, can not create a new prediction!")


        self.__log.debug(f"create_prediction: getting dataset {training['dataset_id']} for training")
        found, dataset = self.get_dataset(user_id, training["dataset_id"])
        if not found:
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {training['dataset_id']} for user {user_id} does not exist, can not create a new prediction!")

        self.__log.debug("create_prediction: inserting new prediction dataset into database...")
        prediction_id = self.__mongo.insert_prediction(user_id, prediction_details)

        upload_file = os.path.join(self.__storage_dir, user_id, "uploads", live_dataset_file_name)
        self.__log.debug(f"create_prediction: upload location is: {upload_file}")
        
        filename_dest = os.path.join(self.__storage_dir, user_id, str(dataset["_id"]), "predictions", prediction_id, live_dataset_file_name)
        self.__log.debug(f"create_prediction: final persistence location is: {filename_dest}")

        self.__log.debug(f"create_prediction: creating dataset folder location: {filename_dest}")
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
        self.__log.debug(f"create_prediction: moving prediction dataset from: {upload_file} to: {filename_dest}")
        shutil.move(upload_file, filename_dest)

        if dataset["type"] == ":image":
            self.__log.debug("create_prediction: dataset is of image type: unzipping, deleting zip archive and remove .zip suffix...")
            shutil.unpack_archive(filename_dest, os.path.join(self.__storage_dir, user_id, str(dataset["_id"]), "predictions", prediction_id))
            os.remove(filename_dest)
            filename_dest = filename_dest.replace(".zip", "")


        self.__log.debug(f"create_prediction: new dataset inserted with id: {prediction_id}")
        success = self.__mongo.update_prediction(user_id, prediction_id, {
            "live_dataset_path": filename_dest
        })
        assert success, f"cannot update dataset with id {prediction_id}"

        return prediction_id

    def update_prediction(self, user_id: str, prediction_id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single dataset with new values. 
        ---
        >>> success: bool = data_storage.UpdateDataset("automl_user", dataset_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. user id: name of the user
        2. dataset id
        3. new values: dict with new values
        4. run analysis: if the dataset analysis should be executed
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        self.__log.debug(f"update_prediction: updating: {prediction_id} for user {user_id}, new values {new_values}")
        return self.__mongo.update_prediction(user_id, prediction_id, new_values)

    def get_prediction(self, user_id: str, prediction_id: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the first dataset with this id 
        ---
        >>> found, dataset = ds.get_dataset("automl_user", "12323asdas")
        >>> if not found:
                print("We have a problem")

        ---
        Parameter
        1. user id 
        2. dataset id
        ---
        Returns either `(True, Dataset)` or `(False, None)`.
        """
        result = self.__mongo.get_prediction(user_id, {
            "_id": ObjectId(prediction_id)
        })

        return result is not None, result

    #def get_datasets(self, user_id: bool):
    def get_predictions(self, user_id: str, model_id: str) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user. 
        ---
        >>> for dataset in data_storage.GetDatasets("automl_user"):
                print(dataset["path"])

        ---
        Parameter
        1. user_id: name of the user
        ---
        Returns `list` of all datasets.
        """
        return [ds for ds in self.__mongo.get_predictions(user_id, {"model_id": model_id})]

    def delete_prediction(self, user_id: str, prediction_id: str):
        """
        Delete a dataset and its associated items
        ---
        Parameter
        1. user id
        2. dataset id
        ---
        Returns amount of deleted objects
        """
        #TODO
        #First check if dataset isn't already deleted
        found, dataset = self.get_prediction(user_id, prediction_id)
        if not found:
            self.__log.error(f"delete_prediction: attempting to delete a dataset that does not exist: {prediction_id} for user {user_id}")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {prediction_id} does not exist, already deleted?")
        path = dataset["path"]
        if os.getenv("WIN_DEV_MACHINE") == "YES":
            path = path.replace( "\\"+ os.path.basename(dataset["path"]), "")
        else:
            path = path.replace( "/"+ os.path.basename(dataset["path"]), "")
        #Before deleting the prediction, delete all related documents
        self.__log.debug(f"delete_prediction: deleting files within path: {path}")
        shutil.rmtree(path)
        amount_deleted_datasets_result = self.__mongo.delete_prediction(user_id, { "prediction_id": prediction_id})
        self.__log.debug(f"delete_prediction: documents deleted within dataset: {amount_deleted_datasets_result}")
        return amount_deleted_datasets_result


#endregion


    

    class __DbLock():
        """
        DataStore internal helper class. Use with `data_store.lock()`
        """
        def __init__(self, inner: Lock):
            self.__inner = inner
            
        def __enter__(self):
            self.__inner.acquire()
            
        def __exit__(self, type, value, traceback):
            self.__inner.release()
