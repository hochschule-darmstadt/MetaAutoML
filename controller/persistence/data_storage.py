import io
import shutil
from threading import Lock
import os
import os.path
from persistence.mongo_client import Database
from bson.objectid import ObjectId
from DataSetAnalysisManager import DataSetAnalysisManager
import pandas as pd
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sktime.datasets import write_dataframe_to_tsfile
from sktime.datasets import load_from_tsfile_to_dataframe

class DataStorage:
    """
    Centralized Access to File System and Database
    """


    def __init__(self, data_storage_dir: str, database = None):
        """
        Initialize new instance. This should be done already.
        Do _not_ use multiple instances of this class.

        Will connect to the MongoDB database defined in docker-compose
        unless `database` is provided.

        >>> data_storage = DataStorage("/tmp/")

        ----
        Parameter
        1. storage directory on disk
        2. optional Database object (used for Testing)
        """
        # ensure folder exists
        os.makedirs(data_storage_dir, exist_ok=True)

        self.__storage_dir = data_storage_dir

        if database is None:
            # assume that we run with docker-compose
            self.__mongo: Database = Database("mongodb://root:example@mongo")
        else:
            self.__mongo: Database = Database(database)

        self.__lock = Lock()


    def Lock(self):
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

    def CheckIfUserExists(self, username: bool):
        """
        Check if user exists by checking if his database exists
        ---
        >>> id: str = ds.CheckIfUserExists("automl_user")
        ---
        Parameter
        1. username: name of the user
        ---
        Returns database existance status, TRUE == EXITS
        """
        return self.__mongo.CheckIfUserExists(username)

    def InsertTraining(self, username: str, training: 'dict[str, object]') -> str:
        """
        Insert single training into the database.
        ---
        >>> id: str = ds.InsertTraining("automl_user", {
                "dataset": ...,
                ...
            })

        ---
        Parameter
        1. username: name of the user
        2. training: training dict to be inserted
        ---
        Returns training id
        """
        return self.__mongo.InsertTraining(username, training)


    def GetTraining(self, username: str, id: str) -> 'dict[str, object]':
        """
        Get single training by id. 
        ---
        >>> sess = data_storage.GetTraining("automl_user", sess_id)
        >>> if sess is None:
                raise Exception("cannot find training")
        
        ---
        Parameter
        1. username: name of the user
        2. id: id of training
        ---
        Returns training as `dict` or `None` if not found.
        """
        return self.__mongo.GetTraining(username, id)

    def GetTrainings(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all trainings for a user. 
        ---
        >>> for sess in data_storage.GetTrainings("automl_user"):
                print(sess["dataset"])

        ---
        Parameter
        1. username: name of the user
        ---
        Returns trainings as `list` of dictionaries.
        """
        return [sess for sess in self.__mongo.GetTrainings(username)]

    def UpdateTraining(self, username: str, id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single training with new values. 
        ---
        >>> success: bool = data_storage.UpdateTraining("automl_user", sess_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. username: name of the user
        2. id: id of training
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.UpdateTraining(username, id, new_values)


    def InsertDataset(self, username: str, fileName: str, type: str, name: str) -> str:
        """
        Store dataset contents on disk and insert entry to database.
        ---
        >>> id: str = ds.InsertDataset("automl_user", "my_dataset", ...)

        ---
        Parameter
        1. username: name of the user
        2. name: name of dataset
        3. content: raw bytes for file on disk
        4. database_content: dictionary for database
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
        dataset_id = self.__mongo.InsertDataset(username, database_content)
        # Upload file to temporary upload folder
        upload_file = os.path.join(self.__storage_dir, username, "uploads", fileName)
        # Get destination filepath using the generated id
        filename_dest = os.path.join(self.__storage_dir, username, dataset_id, fileName)

        if os.getenv("MONGO_DB_DEBUG") != "YES":
            # When not in a debug environment (for example within docker) we do not want to add the app section,
            # as this leads to broken links
            upload_file = upload_file.replace("/app/", "")
            filename_dest = filename_dest.replace("/app/", "")

        # Make sure directory exists in case it's the first upload from this user
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
        # Copy dataset into final folder
        shutil.move(upload_file, filename_dest)
        file_configuration = ""

        # If the dataset is an image dataset, which is always uploaded as a .zip file the images have to be unzipped
        # after saving
        if type == ":image":
            shutil.unpack_archive(filename_dest, os.path.join(self.__storage_dir, username, dataset_id))
            # delete zip
            os.remove(filename_dest)
            # remove .zip suffix of filename and path
            filename_dest = filename_dest.replace(".zip", "")
            fileName = fileName.replace(".zip", "")

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

        if type == ":longitudinal":
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

        nbytes = get_size(os.path.join(self.__storage_dir, username, dataset_id))

        analysis_result = {}
        # If the dataset is a tabular dataset it can be analyzed.
        if type == ":tabular":
            try:
                dsam = DataSetAnalysisManager(pd.read_csv(filename_dest, engine="python"))
            except pd.errors.ParserError as e:
                # As the pandas python parsing engine sometimes fails: Retry with standard (c) parser engine.
                dsam = DataSetAnalysisManager(pd.read_csv(filename_dest))
            analysis_result["basic_analysis"] = dsam.basicAnalysis()
            plot_filepath = os.path.join(os.path.dirname(filename_dest), "plots")
            os.makedirs(plot_filepath, exist_ok=True)
            analysis_result["advanced_analysis"] = dsam.advancedAnalysis(plot_filepath)

        if type == ":longitudinal":
            dataset_for_analysis = load_from_tsfile_to_dataframe(filename_dest, return_separate_X_and_y=False)
            analysis_result["basic_analysis"] = DataSetAnalysisManager.startLongitudinalDataAnalysis(dataset_for_analysis)

        success = self.__mongo.UpdateDataset(username, dataset_id, {
            "path": filename_dest,
            "size": nbytes,
            "mtime": os.path.getmtime(filename_dest),
            "analysis": analysis_result,
            "file_name": fileName,
            "file_configuration": file_configuration
        }, False)
        assert success, f"cannot update dataset with id {dataset_id}"

        return dataset_id

    def UpdateDataset(self, username: str, id: str, new_values: 'dict[str, object]', run_analysis: bool) -> bool:
        """
        Update single dataset with new values. 
        ---
        >>> success: bool = data_storage.UpdateDataset("automl_user", dataset_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. username: name of the user
        2. id: dataset id
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        delimiters = {
            "comma":        ",",
            "semicolon":    ";",
            "space":        " ",
            "tab":          "\t",
        }
        if run_analysis == True:
            found, dataset = self.GetDataset(username, id)
            analysis_result = {}
            # If the dataset is a tabular dataset it can be analyzed.
            if dataset['type'] == ":tabular" or dataset['type'] == ":text" or dataset['type'] == ":time_series":
                #Delete old references
                new_values["analysis"] = ""
                self.__mongo.UpdateDataset(username, id, new_values)
                file_config = json.loads(dataset["file_configuration"])
                dsam = DataSetAnalysisManager(pd.read_csv(dataset['path'], delimiter=delimiters[file_config['delimiter']], skiprows=(file_config['start_row']-1), escapechar=file_config['escape_character'], decimal=file_config['decimal_character']))
                analysis_result["basic_analysis"] = dsam.basicAnalysis()
                plot_filepath = os.path.join(os.path.dirname(dataset['path']), "plots")
                os.makedirs(plot_filepath, exist_ok=True)
                analysis_result["advanced_analysis"] = dsam.advancedAnalysis(plot_filepath)
                new_values["analysis"] = analysis_result

        return self.__mongo.UpdateDataset(username, id, new_values)


    def GetDataset(self, username: str, identifier: str) -> 'tuple[bool, dict[str, object]]':
        """
        Try to find the _first_ dataset with this name. 
        ---
        >>> found, dataset = ds.GetDataset("automl_user", "my_dataset")
        >>> if not found:
                print("We have a problem")

        ---
        Parameter
        1. username: name of the user
        2. name: name of dataset
        ---
        Returns either `(True, Dataset)` or `(False, None)`.
        """
        result = self.__mongo.GetDataset(username, {
            "_id": ObjectId(identifier)
        })

        return result is not None, result


    def GetDatasets(self, username: str) -> 'list[dict[str, object]]':
        """
        Get all datasets for a user. 
        ---
        >>> for dataset in data_storage.GetDatasets("automl_user"):
                print(dataset["path"])

        ---
        Parameter
        1. username: name of the user
        ---
        Returns `list` of all datasets.
        """
        return [ds for ds in self.__mongo.GetDatasets(username)]


    def InsertModel(self, username: str, model: 'dict[str, object]') -> str:
        """
        Insert single model into the database.
        ---
        >>> mdl_id: str = data_storage.InsertModel("automl_user", {
                "automl_name": "MLJAR",
                "training_id": training_id,
                ...
            })

        ---
        Parameter
        1. username: name of the user
        2. model: dict of model data 
        ---
        Returns id of new model.
        """
        return self.__mongo.InsertModel(username, model)

    def UpdateModel(self, username: str, id: str, new_values: 'dict[str, object]') -> bool:
        """
        Update single model with new values. 
        ---
        >>> success: bool = data_storage.UpdateModel("automl_user", model_id, {
                "status": "completed"
            })

        ---
        Parameter
        1. username: name of the user
        2. id: model id
        3. new_values: dict with new values
        ---
        Returns `True` if successfully updated, otherwise `False`.
        """
        return self.__mongo.UpdateModel(username, id, new_values)

    def GetModels(self, username: str, training_id: str = None, dataset_id: str = None) -> 'list[dict[str, object]]':
        """
        Get all models, or all models by training id or dataset id
        ---
        >>> models = ds.GetModels("automl_user", "training_id")

        ---
        Parameter
        1. username: name of the user
        2. training_id: optinal training id
        2. dataset_id: optinal dataset id
        ---
        Returns a models list
        """
        if training_id != None:
            filter = { "training_id": training_id }
        elif dataset_id != None:
            filter = { "dataset_id": dataset_id }
        else:
            filter = None
        result = self.__mongo.GetModels(username, filter)

        return [ds for ds in result]

    def GetModel(self, username: str, model_id: str = None) -> 'dict[str, object]':
        """
        Get models by model id
        ---
        >>> models = ds.GetModel("automl_user", "model_id")

        ---
        Parameter
        1. username: name of the user
        2. model_id: optinal model id
        ---
        Returns a models list
        """
        return self.__mongo.GetModel(username, model_id)


    class __DbLock():
        """
        DataStore internal helper class. Use with `data_store.lock()`
        """
        def __init__(self, inner: Lock):
            self.__inner = inner
            
        def __enter__(self):
            self.__inner.acquire()
            
        def __exit__(self, type, value, traceback):
            self.__inner .release()
