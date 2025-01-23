import os, shutil, logging
from MongoDbClient import MongoDbClient
from sklearn.model_selection import train_test_split
from sktime.datasets import load_from_tsfile_to_dataframe
import pandas as pd
from bson.objectid import ObjectId
from ControllerBGRPC import *
from threading import Lock
from datetime import datetime, timedelta
from scipy.io import arff

class DataStorage:
    """
    Centralized Access to File System and Database
    """
    def __init__(self, data_storage_dir: str, mongo_db: MongoDbClient = None):
        """Initialize a new DataStorage instance.

        Args:
            data_storage_dir (str): Directory path which the data storage uses as base to save data
            mongo_db (MongoDbClient, optional): Mongodb client used to interact with the mongodb. Defaults to None.
        """
        self.__log = logging.getLogger('DataStorage')
        self.__log.setLevel(logging.getLevelName(os.getenv("PERSISTENCE_LOGGING_LEVEL")))
        # ensure folder exists
        os.makedirs(data_storage_dir, exist_ok=True)
        self.__storage_dir = data_storage_dir
        #self.__mongo_db_url = mongo_db_url
        self.__mongo: MongoDbClient = mongo_db
        self.__lock = Lock()
        self.__frontend_backend_encoding_conversion_table = {
            "ascii": "ascii",
            "utf-8": "utf_8",
            "utf-16": "utf_16",
            "utf-16le": "utf_16_le",
            "utf-16be": "utf_16_be",
            "utf-32": "utf_32",
            "windows-1252" : "cp1252",
            "iso-8859-1": "latin-1",
            "latin-1": "latin-1",
            "": ""
        }

    ####################################
    ## MISC DATASTORAGE OPERATIONS
    ####################################
#region
    def get_home_overview_information(self, user_id: str) -> 'GetHomeOverviewInformationResponse':
        """Get information for the home overview page of a user (# datasets, trainings, models, active trainings)

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend

        Returns:
            GetHomeOverviewInformationResponse: The GRPC response message holding the infos for the home overview
        """
        return self.__mongo.get_home_overview_information(user_id)


    def check_if_user_exists(self, user_id: bool) -> bool:
        """Check if user already exists by checking if a database with his user id exists.

        Args:
            user_id (bool): Unique user id saved within the MS Sql database of the frontend

        Returns:
            bool: True if the user exists, False if the user does not exists
        """
        return self.__mongo.check_if_user_exists(user_id)


    def lock(self):
        """Lock access to the data storage to a single thread.
        ---
        >>> with data_store.lock():
                # critical region
                sess = data_storage.get_session(...)
                data_storage.update_session(..., {
                    "models": sess["models"] + [new_model]
                })

        Returns:
            __DbLock: datastorage internal lock
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

    def __convert_arff_to_csv(self, user_id: str, file_name: str) -> str:
        """Convert arff file to csv file

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            file_name (str): Uploaded file name within the users upload folder

        Returns:
            str: The converted csv file name
        """
        arff_file = os.path.join(self.__storage_dir, user_id, "uploads", file_name)
        file_name = file_name.replace(".arff", ".csv")
        csv_file = os.path.join(self.__storage_dir, user_id, "uploads", file_name)
        try:
            data, _ = arff.loadarff(arff_file)
            df = pd.DataFrame(data)
            categories = [col for col in df.columns if df[col].dtype=="O"]
            df[categories]=df[categories].apply(lambda x: x.str.decode('utf8'))
            df.to_csv(csv_file, index=False)
            os.remove(arff_file)
            return file_name

        # String attributes in arff are not supported by scipy, try to convert arff file to csv manually
        except NotImplementedError:
            in_data_section = False
            header = ""
            data_content = []
            with open(arff_file, "r") as in_file:
                content = in_file.readlines()
                for line in content:
                    if not in_data_section:
                        # Check if the line contains attribute information
                        if "@ATTRIBUTE" in line.upper():
                            attributes = line.split()
                            column_name = attributes[1]
                            header += column_name.replace("'", "") + ","
                        elif "@DATA" in line.upper():
                            in_data_section = True
                            header = header[:-1]
                            header += '\n'
                            data_content.append(header)
                    else:
                        data_content.append(line)
            with open(csv_file, "w") as out_file:
                out_file.writelines(data_content)
            os.remove(arff_file)
            return file_name

    def __convert_excel_to_csv(self, user_id: str, file_name: str) -> str:
        """Convert excel file (.xlsx and .xls) to csv file

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            file_name (str): Uploaded file name within the users upload folder

        Returns:
            str: The converted csv file name
        """
        excel_file = os.path.join(self.__storage_dir, user_id, "uploads", file_name)
        file_name = file_name.replace(".xlsx", ".csv").replace(".xls", ".csv")
        csv_file = os.path.join(self.__storage_dir, user_id, "uploads", file_name)
        df = pd.read_excel(excel_file)
        df.to_csv(csv_file, index=False)
        os.remove(excel_file)
        return file_name


    def create_dataset(self, user_id: str, file_name: str, type: str, name: str, encoding: str) -> str:
        """Create new dataset record and move dataset from upload folder to final path

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            file_name (str): Uploaded file name within the users upload folder
            type (str): The selected dataset type
            name (str): User defined name used when displaying the dataset
            encoding (str): Automatically detected encoding

        Returns:
            str: The new dataset record id
        """
        if type == ":image":
            self.__log.debug(f"create_dataset: dataset type is image, removing .zip ending from {name} as not necessary after unzipping anymore...")
            name = name.replace(".zip", "")

        file_extension = file_name.split(".")[-1]
        if file_extension == "arff":
            file_name = self.__convert_arff_to_csv(user_id, file_name)
        elif file_extension in ["xlsx", "xls"]:
            file_name = self.__convert_excel_to_csv(user_id, file_name)

        # build dictionary for database
        database_content = {
            "name": name,
            "type": type,
            "path": "",
            "schema": {},
            "training_ids": [],
            "analysis": {
                "creation_date": 0,
                "size_bytes": 0,
                "report_html_path": "",
                "report_json_path": ""
            },
            "lifecycle_state": "active"
        }

        self.__log.debug("create_database: creating a new database...")
        self.__mongo.create_database(user_id)
        self.__log.debug(f"create_database: new database created for user with id: {user_id}")

        self.__log.debug("create_dataset: inserting new dataset into database...")
        dataset_id = self.__mongo.insert_dataset(user_id, database_content)
        self.__log.debug(f"create_dataset: new dataset inserted with id: {dataset_id}")

        upload_file = os.path.join(self.__storage_dir, user_id, "uploads", file_name)
        self.__log.debug(f"create_dataset: upload location is: {upload_file}")

        filename_dest = os.path.join(self.__storage_dir, user_id, dataset_id, file_name)
        self.__log.debug(f"create_dataset: final persistence location is: {filename_dest}")

        self.__log.debug(f"create_dataset: creating dataset folder location: {filename_dest}")
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
        self.__log.debug(f"create_dataset: moving dataset from: {upload_file} to: {filename_dest}")
        shutil.move(upload_file, filename_dest)
        file_configuration = {}

        if type == ":image":
            self.__log.debug("create_dataset: dataset is of image type: unzipping, deleting zip archive and remove .zip suffix...")
            dataset_dir = os.path.join(self.__storage_dir, user_id, dataset_id)
            shutil.unpack_archive(filename_dest, dataset_dir)
            # Cleanup: remove zip archive and __MACOSX folder on MacOS
            os.remove(filename_dest)
            macosx_folder = os.path.join(dataset_dir, '__MACOSX')
            if os.path.exists(macosx_folder) and os.path.isdir(macosx_folder):
                shutil.rmtree(macosx_folder)
            extracted_items = os.listdir(dataset_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(dataset_dir, extracted_items[0])):
                filename_dest = os.path.join(dataset_dir, extracted_items[0])
            else:
                filename_dest = filename_dest.replace(".zip", "")

        if type == ":tabular" or type == ":text" or type == ":time_series":
            #generate preview of tabular and text dataset
            #previewDf = pd.read_csv(filename_dest)
            #previewDf.head(50).to_csv(filename_dest.replace(".csv", "_preview.csv"), index=False)
            #causes error with different delimiters use normal string division
            self.__log.debug("create_dataset: dataset is of CSV type: generating csv file configuration...")
            file_configuration = {"use_header": True, "start_row":1, "delimiter":"comma", "escape_character":"\\", "decimal_character":".", "encoding": self.__frontend_backend_encoding_conversion_table[encoding], "thousands_seperator": "", "datetime_format": "%d-%m-%Y %H:%M:%S"}

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
            file_configuration = {"use_header": True, "start_row":1, "delimiter":"comma", "escape_character":"\\", "decimal_character":".", "encoding": self.__frontend_backend_encoding_conversion_table[encoding], "thousands_seperator": "", "datetime_format": "%Y-%m-%d  %H:%M:%S"}

        success = self.__mongo.update_dataset(user_id, dataset_id, {
            "path": filename_dest,
            "file_configuration": file_configuration
        })
        assert success, f"cannot update dataset with id {dataset_id}"

        return dataset_id

    def update_dataset(self, user_id: str, dataset_id: str, new_values: 'dict[str, object]') -> bool:
        """Update single dataset record with new values
        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            dataset_id (str): The dataset id of the dataset record which is to be updated
            new_values (dict[str, object]): Dictonary of new dataset record field values that will be updated

        Returns:
            bool: True if the record was updated, False if the record was not updated
        """
        self.__log.debug(f"update_dataset: updating: {dataset_id} for user {user_id}, new values {new_values}")
        return self.__mongo.update_dataset(user_id, dataset_id, new_values)

    def get_dataset(self, user_id: str, dataset_id: str) -> 'tuple[bool, dict[str, object]]':
        """Get a dataset record by id from a specific user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            dataset_id (str): The dataset id of the dataset record which is to be updated

        Returns:
            tuple[bool, dict[str, object]]: Tuple first identifying if a dataset record was found and secondly the dataset record (`(True, Dataset)` or `(False, None)`)
        """
        result = self.__mongo.get_dataset(user_id, {
            "_id": ObjectId(dataset_id),
            "lifecycle_state": "active"
        })

        return result is not None, result

    def get_datasets(self, user_id: str, only_five_recent:bool=False, pagination:bool=False, page_number:int=1) -> 'list[dict[str, object]]':
        """Get all dataset records from a specific user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend

        Returns:
            list[dict[str, object]]: List of all available dataset records
        """

        return [ds for ds in self.__mongo.get_datasets(user_id, {"lifecycle_state": "active"}, only_five_recent=only_five_recent, page_number=page_number, pagination=pagination)]

    def delete_dataset(self, user_id: str, dataset_id: str) -> int:
        """Delete a dataset record by id from a user databse. (all related record and files will also be deleted (Trainings, Models, Predictions))

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            dataset_id (str): The dataset id of the dataset record which is to be updated

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the to be deleted dataset does not exist inside MongoDB

        Returns:
            int: The amount of dataset records deleted (should always be 1)
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
        existing_trainings = self.get_trainings_metadata(user_id, dataset_id)
        self.__log.debug(f"delete_dataset: deleting {existing_trainings.count} trainings")
        for training in existing_trainings:
            try:
                self.delete_training(user_id, str(training["id"]))
            except:
                self.__log.debug(f"delete_dataset: deleting training failed, already deleted. Skipping...")
        self.__log.debug(f"delete_dataset: deleting files within path: {path}")
        shutil.rmtree(path)
        amount_deleted_datasets_result = self.__mongo.delete_dataset(user_id, dataset_id)
        self.__log.debug(f"delete_dataset: documents deleted within dataset: {amount_deleted_datasets_result}")
        return amount_deleted_datasets_result


#endregion

    ####################################
    ## MODEL RELATED OPERATIONS
    ####################################
#region


    def create_model(self, user_id: str, model_details: 'dict[str, object]') -> str:
        """Create new model record inside MongoDB

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model_details (dict[str, object]): Dictonary of model record fields (see data schema in WIKI for more information)

        Returns:
            str: The new model record id
        """
        return self.__mongo.insert_model(user_id, model_details)

    def update_model(self, user_id: str, model_id: str, new_values: 'dict[str, object]') -> bool:
        """Update single model record with new values

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model_id (str): The model id of the model record which is to be updated
            new_values (dict[str, object]): Dictonary of new model record field values that will be updated

        Returns:
            bool: True if the record was updated, False if the record was not updated
        """
        return self.__mongo.update_model(user_id, model_id, new_values)

    def get_model(self, user_id: str, model_id: str) -> 'tuple[bool, dict[str, object]]':
        """Get a model record by id from a specific user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model_id (str, optional): The model id of the model record which is to be updated

        Returns:
            tuple[bool, dict[str, object]]: Tuple first identifying if a model record was found and secondly the model record (`(True, Model)` or `(False, None)`)
        """
        result = self.__mongo.get_model(user_id, {
            "_id": ObjectId(model_id),
            "lifecycle_state": "active"
        })

        return result is not None, result

    def get_models(self, user_id: str, training_id: str = None, dataset_id: str = None) -> 'list[dict[str, object]]':
        """Get all model records from a specific user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            training_id (str, optional): Set a filter to get model records by training id. Defaults to None.
            dataset_id (str, optional): Set a filter to get model records by dataset id. Defaults to None.

        Returns:
            list[dict[str, object]]: List of all available model records
        """
        if training_id is not None:
            filter = { "training_id": training_id, "lifecycle_state": "active" }
        elif dataset_id is not None:
            found, dataset = self.get_dataset(user_id, dataset_id)
            filter = { "training_id": { '$in': dataset["training_ids"] }, "lifecycle_state": "active" }
        else:
            filter = {"lifecycle_state": "active"}
        result = self.__mongo.get_models(user_id, filter)

        return [ds for ds in result]

    def delete_model(self, user_id: bool, model_id: str) -> int:
        """Delete a model record by id from a user databse. (all related record and files will also be deleted (Predictions))

        Args:
            user_id (bool): Unique user id saved within the MS Sql database of the frontend
            model_id (str): The model id of the dataset record which is to be updated

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the to be deleted model does not exist inside MongoDB
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the to be model files do not exist on the disk anymore (model will still be deleted from MongoDB)

        Returns:
            int: The amount of model records deleted (should always be 1)
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
            amount_deleted_models = self.__mongo.delete_model(user_id, model_id)
        except:
            self.__log.error(f"delete_model: deleting files within path: {path} failed, path does not exist")
            amount_deleted_models = self.__mongo.delete_model(user_id, model_id)
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {model_id} file path does not exist, already deleted?")

        return amount_deleted_models

#endregion

    ####################################
    ## TRAINING RELATED OPERATIONS
    ####################################
#region

    def create_training(self, user_id: str, training_details: 'dict[str, object]') -> str:
        """
        Create new training record inside MongoDB

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            training_details (dict[str, object]): Dictonary of training record fields (see data schema in WIKI for more information)

        Returns:
            str: The new training record id
        """
        return self.__mongo.insert_training(user_id, training_details)

    def update_training(self, user_id: str, training_id: str, new_values: 'dict[str, object]') -> bool:
        """Update single training record with new values

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            training_id (str): The training id of the training record which is to be updated
            new_values (dict[str, object]): Dictonary of new training record field values that will be updated

        Returns:
            bool: True if the record was updated, False if the record was not updated
        """
        return self.__mongo.update_training(user_id, training_id, new_values)

    def get_training(self, user_id: str, training_id: str) -> 'tuple[bool, dict[str, object]]':
        """Get a training record by id from a specific user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            training_id (str, optional): The training id of the training record which is to be updated

        Returns:
            tuple[bool, dict[str, object]]: Tuple first identifying if a training record was found and secondly the training record (`(True, Training)` or `(False, None)`)
        """
        result = self.__mongo.get_training(user_id, {
            "_id": ObjectId(training_id),
            "lifecycle_state": "active"
        })

        return result is not None, result

    def get_trainings_metadata(self, user_id: str, dataset_id:str=None, only_last_day:bool=False, pagination:bool=False, page_number:int=1, page_size:int=20, filter:object={}) -> 'list[dict[str, object]]':
        """Get all training records from a specific user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            dataset_id (str, optional): Set a filter to get training records by dataset id. Defaults to None.
            pagination (bool): If pagination is used
            page_number (int): the pagination page to retrieve
            page_size (int): the number of records per page
            search_string (str, optional): The search string to filter the records. Defaults to None.
            sort_label (str, optional): The label to sort the records. Defaults to None.
            sort_direction (str, optional): The direction to sort the records. Defaults to None.

        Returns:
            list[dict[str, object]]: List of all available training records
        """
        search_filter = {"lifecycle_state": "active"}
        search_filter.update(filter)
        if dataset_id is not None:
            search_filter.update({"dataset_id": dataset_id})
        if only_last_day:
            now = datetime.now()
            yesterday = now - timedelta(hours=24)
            search_filter.update({
                "runtime_profile.start_time": {
                    "$gte": yesterday,
                    "$lt": now
                }
            })
        return [sess for sess in self.__mongo.get_trainings_metadata(user_id, search_filter, pagination, page_number, page_size)]

    def delete_training(self, user_id: bool, training_id: str) -> int:
        """Delete a training record by id from a user databse. (all related record and files will also be deleted (Models, Predictions))

        Args:
            user_id (bool): Unique user id saved within the MS Sql database of the frontend
            training_id (str): The training id of the dataset record which is to be updated

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the to be deleted training does not exist inside MongoDB

        Returns:
            int: The amount of training records deleted (should always be 1)
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
        amount_deleted_trainings_result = self.__mongo.delete_training(user_id, training_id)
        self.__log.debug(f"delete_training: documents deleted within training: {amount_deleted_trainings_result}")
        return amount_deleted_trainings_result

    def get_trainings_count(self, user_id: str) -> int:
        """Get the total number of training records for a user

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend

        Returns:
            int: The total number of training records
        """
        return self.__mongo.get_trainings_count(user_id)

#endregion

    ####################################
    ## PREDICTION RELATED OPERATIONS
    ####################################
#region

    def create_prediction(self, user_id: str, live_dataset_file_name: str, prediction_details: 'dict[str, object]') -> str:
        """Create new prediction record inside MongoDB

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            live_dataset_file_name (str): File name within the upload folder of the uploaded live dataset file
            prediction_details (dict[str, object]): Dictonary of prediction record fields (see data schema in WIKI for more information)

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the the related model does not exist inside MongoDB
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the the related training does not exist inside MongoDB
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the the related dataset does not exist inside MongoDB

        Returns:
            str: The new prediction record id
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

        self.__log.debug("create_prediction: adding prediction id to model prediction ids...")
        self.__mongo.update_model(user_id, prediction_details['model_id'], {"prediction_ids": model["prediction_ids"] + [prediction_id]})

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
        """Update single prediction record with new values

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            prediction_id (str): The prediction id of the prediction record which is to be updated
            new_values (dict[str, object]): Dictonary of new prediction record field values that will be updated

        Returns:
            bool: True if the record was updated, False if the record was not updated
        """
        self.__log.debug(f"update_prediction: updating: {prediction_id} for user {user_id}, new values {new_values}")
        return self.__mongo.update_prediction(user_id, prediction_id, new_values)

    def get_prediction(self, user_id: str, prediction_id: str) -> 'tuple[bool, dict[str, object]]':
        """Get a prediction record by id from a specific user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            prediction_id (str, optional): The prediction id of the prediction record which is to be updated

        Returns:
            tuple[bool, dict[str, object]]: Tuple first identifying if a prediction record was found and secondly the prediction record (`(True, Prediction)` or `(False, None)`)
        """
        result = self.__mongo.get_prediction(user_id, {
            "_id": ObjectId(prediction_id),
            "lifecycle_state": "active"
        })

        return result is not None, result

    #def get_datasets(self, user_id: bool):
    def get_predictions(self, user_id: str, model_id: str) -> 'list[dict[str, object]]':
        """Get all prediction records from a specific user database

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model_id (str, optional): Set a filter to get prediction records by model id. Defaults to None.

        Returns:
            list[dict[str, object]]: List of all available prediction records
        """
        return [ds for ds in self.__mongo.get_predictions(user_id, {"model_id": model_id, "lifecycle_state": "active"})]

    def delete_prediction(self, user_id: str, prediction_id: str) -> int:
        """Delete a prediction record by id from a user databse.

        Args:
            user_id (bool): Unique user id saved within the MS Sql database of the frontend
            prediction_id (str): The prediction id of the dataset record which is to be updated

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND is raised when the to be deleted prediction does not exist inside MongoDB

        Returns:
            int: The amount of prediction records deleted (should always be 1)
        """
        #First check if dataset isn't already deleted
        found, dataset = self.get_prediction(user_id, prediction_id)
        if not found:
            self.__log.error(f"delete_prediction: attempting to delete a dataset that does not exist: {prediction_id} for user {user_id}")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Dataset {prediction_id} does not exist, already deleted?")
        try:
            path = dataset["live_dataset_path"]
            if os.getenv("WIN_DEV_MACHINE") == "YES":
                path = path.replace( "\\"+ os.path.basename(dataset["path"]), "")
            else:
                path = path.replace( "/"+ os.path.basename(dataset["path"]), "")
            #Before deleting the prediction, delete all related documents
            self.__log.debug(f"delete_prediction: deleting files within path: {path}")
            shutil.rmtree(path)
        except:
            self.__log.debug(f"delete_prediction: deleting files within path: {path} failed, path unknown")
        amount_deleted_datasets_result = self.__mongo.delete_prediction(user_id, prediction_id)
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
