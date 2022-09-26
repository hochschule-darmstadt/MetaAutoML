import os, shutil, logging
import threading 
from MongoDbClient import MongoDbClient
from sklearn.model_selection import train_test_split
from sktime.datasets import write_dataframe_to_tsfile
from sktime.datasets import load_from_tsfile_to_dataframe
import pandas as pd
from bson.objectid import ObjectId
from DataSetAnalysisManager import DataSetAnalysisManager
from controller_bgrpc import *

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
            # replace zip sufix with nothing as it will be unpacked
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

        # Get generated dataset_id from mongo
        dataset_id = self.__mongo.InsertDataset(user_identifier, database_content)
        # Upload file to temporary upload folder
        upload_file = os.path.join(self.__storage_dir, user_identifier, "uploads", file_name)
        # Get destination filepath using the generated id
        filename_dest = os.path.join(self.__storage_dir, user_identifier, dataset_id, file_name)

        #if os.getenv("MONGO_DB_DEBUG") != "YES":
            # When not in a debug environment (for example within docker) we do not want to add the app section,
            # as this leads to broken links
            #upload_file = upload_file.replace("/app/", "")
            #filename_dest = filename_dest.replace("/app/", "")

        # Make sure directory exists in case it's the first upload from this user
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
        # Copy dataset into final folder
        shutil.move(upload_file, filename_dest)
        file_configuration = ""

        # If the dataset is an image dataset, which is always uploaded as a .zip file the images have to be unzipped
        # after saving
        if type == ":image":
            shutil.unpack_archive(filename_dest, os.path.join(self.__storage_dir, user_identifier, dataset_id))
            # delete zip
            os.remove(filename_dest)
            # remove .zip suffix of filename and path
            filename_dest = filename_dest.replace(".zip", "")
            fileName = file_name.replace(".zip", "")

        if type == ":tabular" or type == ":text" or type == ":time_series":
            #generate preview of tabular and text dataset
            #previewDf = pd.read_csv(filename_dest)
            #previewDf.head(50).to_csv(filename_dest.replace(".csv", "_preview.csv"), index=False)
            #causes error with different delimiters use normal string division
            with open(filename_dest, encoding="utf8") as file:
                lines = file.readlines()
            with open(filename_dest.replace(".csv", "_preview.csv"), "x") as preview:
                preview_line = lines[:51]
                for line in preview_line:
                    preview.write(line)
                    # preview.write("\n")
            file_configuration = '{"use_header":true, "start_row":1, "delimiter":"comma", "escape_character":"\\\\", "decimal_character":"."}'

        if type == ":time_series_longitudinal":
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

        nbytes = get_size(os.path.join(self.__storage_dir, user_identifier, dataset_id))

        analysis_result = {}
        # If the dataset is a certain type the dataset can be analyzed.
        if type in [":tabular", ":text", ":time_series", ":time_series_longitudinal"]:
            analysis_result = DataSetAnalysisManager({"path": filename_dest,
                                                      "file_configuration": file_configuration,
                                                      "type": type}).analysis()

        success = self.__mongo.UpdateDataset(user_identifier, dataset_id, {
            "path": filename_dest,
            "size": nbytes,
            "mtime": os.path.getmtime(filename_dest),
            "analysis": analysis_result,
            "file_name": file_name,
            "file_configuration": file_configuration
        })
        assert success, f"cannot update dataset with id {dataset_id}"

        return dataset_id

    def update_dataset(self, user_identifier: str, id: str, new_values: 'dict[str, object]', run_analysis: bool) -> bool:
        """
        Update single dataset with new values. 
        ---
        >>> success: bool = data_storage.UpdateDataset("automl_user", dataset_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. user_identifier: name of the user
        2. id: dataset id
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        if run_analysis == True:

            found, dataset = self.GetDataset(user_identifier, id)

            # If the dataset is a tabular dataset it can be analyzed.
            if dataset['type'] in [":tabular", ":text", ":time_series", ":time_series_longitudinal"]:
                # Delete old references
                new_values["analysis"] = ""
                self.__mongo.UpdateDataset(user_identifier, id, new_values)
                new_values["analysis"] = DataSetAnalysisManager(dataset).analysis()

        return self.__mongo.UpdateDataset(user_identifier, id, new_values)


    def get_dataset(self, user_identifier: str, dataset_identifier: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the _first_ dataset with this name. 
        ---
        >>> found, dataset = ds.GetDataset("automl_user", "my_dataset")
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
        found, dataset = self.get_dataset(user_identifier, dataset_identifier)
        if not found:
            self.__log.error(f"delete_dataset: attempting to delete a dataset that does not exist: {dataset_identifier} for user {user_identifier}")
            raise grpclib.GRPCError(grpclib.Status.UNKNOWN, "Dataset does not exist, already deleted?")
        path = dataset["path"]
        path = path.replace("\\"+ dataset["file_name"], "")
        #Before delete the dataset, delete all related documents
        amount_deleted_trainings_result = self.__mongo.delete_training(user_identifier, { "dataset_id": dataset_identifier})
        self.__log.debug(f"delete_dataset: documents deleted within training: {amount_deleted_trainings_result.deleted_count}")
        shutil.rmtree(path)
        self.__log.debug(f"delete_dataset: deleting files within path: {path}")
        amount_deleted_datasets_result = self.__mongo.delete_dataset(user_identifier, { "dataset_id": dataset_identifier})
        self.__log.debug(f"delete_dataset: documents deleted within dataset: {amount_deleted_datasets_result.deleted_count}")
        return amount_deleted_datasets_result.deleted_count


        
        
    def delete_training(self, user_identifier: bool, training_identifier: str):
        """
        Delete a training and its associated items
        ---
        Parameter
        1. user identifier
        2. id: object id
        ---
        Returns amount of deleted objects
        """
        amount_deleted_trainings_result = self.__mongo.delete_training(user_identifier, { "_id": ObjectId(training_identifier) })
        self.__log.debug(f"delete_training: documents deleted within training: {amount_deleted_trainings_result.deleted_count}")
        return amount_deleted_trainings_result.deleted_count