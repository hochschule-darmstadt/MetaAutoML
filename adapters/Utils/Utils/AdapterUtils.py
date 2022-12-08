from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
import json
import os
import shutil
import subprocess
import sys
import time, datetime
from typing import Any
import dill
import numpy as np
import pandas as pd
from predict_time_sources import DataType, SplitMethod, feature_preparation
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.metrics import classification_report
from JsonUtil import get_config_property
from TemplateGenerator import TemplateGenerator
import glob
from PIL import Image
from AdapterBGRPC import *
from typing import Tuple

######################################################################
## GRPC HELPER FUNCTIONS
######################################################################

#region

def get_except_response(e: Exception) -> "GetAutoMlStatusResponse":
    """Generate a GRPC status message holding the raised exception informations

    Args:
        e (Exception): The raised exception

    Returns:
        GetAutoMlStatusResponse: The GRPC response message
    """
    print(e)
    response = GetAutoMlStatusResponse()
    response.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_ERROR
    return response


def capture_process_output(process: subprocess.Popen, use_error: bool):
    """Read the console log from the AutoML subprocess until no new text is produced by the subprocess, and yield AutoML status messages

    Args:
        process (subprocess.Popen): The AutoML subprocess instance
        use_error (bool): If instead of the STD OUT the STD ERR is used as input to capture from

    Yields:
        Iterator[GetAutoMlStatusResponse]: The latest Grpc response message generated from reading the subprocess console
    """
    s = ""
    capture = ""
    if(use_error == False):
        s = process.stdout.read(1)
    else:
        s = process.stderr.read(1)
    capture += s
    # Run until no more output is produced by the subprocess
    while len(s) > 0:
        if capture[len(capture) - 1] == '\n':
            process_update = GetAutoMlStatusResponse()
            process_update.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_STATUS_UPDATE
            process_update.status_update = capture
            # if return Code is ADAPTER_RETURN_CODE_STATUS_UPDATE we do not have score values yet
            process_update.test_score = 0.0
            process_update.prediction_time = 0.0
            process_update.ml_library = ""
            process_update.ml_model_type = ""
            yield process_update

            sys.stdout.write(capture)
            sys.stdout.flush()
            capture = ""
        if(use_error == False):
            s = process.stdout.read(1)
        else:
            s = process.stderr.read(1)
        capture += s

    if use_error:
        process.stderr.close()
    else:
        process.stdout.close()

def get_response(config: "StartAutoMlRequest", test_score: float, prediction_time: float, library: str, model: str) -> "GetAutoMlStatusResponse":
    """Generate the final GRPC AutoML status message

    Args:
        config (StartAutoMlRequest): The StartAutoMlRequest request, extended with the trainings folder paths
        test_score (float): The test score archieve by the model
        prediction_time (float): The passed time to make one prediction using the model
        library (str): The ML library the model is based upon
        model (str): The ML model type the model is composed off

    Returns:
        GetAutoMlStatusResponse: The GRPS AutoML status messages
    """
    response = GetAutoMlStatusResponse()
    response.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_SUCCESS
    if get_config_property("local_execution") == "NO":
        response.path = os.path.join(config.controller_export_folder_location, config.file_name)
    else:
        response.path = os.path.join(config.file_location, config.file_name)
    response.test_score = test_score
    response.prediction_time = prediction_time
    response.ml_library = library
    response.ml_model_type = model
    return response


#endregion

######################################################################
## GENERAL HELPER FUNCTIONS
######################################################################

#region

def data_loader(config: "StartAutoMlRequest") -> Any:
    """Load the dataframes for the requested dataset, by loading them into different DataFrames. See Returns section for more information.

    Args:
        config (StartAutoMlRequest): The StartAutoMlRequest request, extended with the trainings folder paths

    Returns:
        Any: Depending on the dataset type: CSV data: tuple[DataFrame (Train), DataFrame (Test)], image data: tuple[DataFrame (X_train), DataFrame (y_train), DataFrame (X_test), DataFrame (y_test)]
    """

    train_data = None
    test_data = None

    if config["configuration"]["task"] in [":tabular_classification", ":tabular_regression", ":text_classification", ":time_series_forecasting", ":time_series_classification"]:
        return read_tabular_dataset_training_data(config)
    elif config["configuration"]["task"] in [":image_classification", ":image_regression"]:
        return read_image_dataset(config)
    return train_data, test_data


def export_model(model: Any, path: str, file_name: str):
    """Export a model instance to disc by using dill

    Args:
        model (Any): The AutoML solutions model instance
        path (str): The absolute folder path where to save the model to
        file_name (str): The file name for the saved model
    """
    with open(os.path.join(path, file_name), 'wb+') as file:
        dill.dump(model, file)


def start_automl_process(config: "StartAutoMlRequest") -> subprocess.Popen:
    """Start the AutoML subprocess

    Args:
        config (StartAutoMlRequest): The StartAutoMlRequest request, extended with the trainings folder paths

    Returns:
        subprocess.Popen: The AutoML subprocess instance
    """
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    return subprocess.Popen([python_env, "AutoML.py", config.job_folder_location],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)

def generate_script(config: "StartAutoMlRequest") -> None:
    """Generate the Python script allowing the independent execution of the model

    Args:
        config (StartAutoMlRequest): The StartAutoMlRequest request, extended with the trainings folder paths
    """
    generator = TemplateGenerator(config)
    generator.generate_script()

def zip_script(config: "StartAutoMlRequest"):
    """Zip the model and generated script together, to a single file which the user can download

    Args:
        config (StartAutoMlRequest): The StartAutoMlRequest request, extended with the trainings folder paths

    Returns:
        StartAutoMlRequest: The StartAutoMlRequest request, extended with addition informations about the saved archive
    """
    print(f"saving model zip file for {get_config_property('adapter-name')}")

    zip_file_name = get_config_property("export-zip-file-name")
    output_path = config.export_folder_location
    result_path = config.result_folder_location
    shutil.copy(get_config_property("predict-time-sources-path"),
                result_path)

    shutil.make_archive(os.path.join(output_path, zip_file_name),
                        'zip',
                        result_path,
                        base_dir=None)

    if get_config_property("local_execution") == "YES":
        file_loc_on_controller = output_path
    else:
        file_loc_on_controller = os.path.join(get_config_property("training-path"),
                                            get_config_property('adapter-name'),
                                        config.user_id,
                                        config.training_id,
                                        get_config_property("export-folder-name"))
    config.file_name = f'{zip_file_name}.zip'
    config.file_location = file_loc_on_controller
    return config

def evaluate(config: "StartAutoMlRequest", config_path: str) -> Tuple[float, float]:
    """Evaluate the model by executing the Python script to compute the test score and prediction time metric

    Args:
        config (StartAutoMlRequest): The StartAutoMlRequest request, extended with addition informations about the saved archive
        config_path (str): The path to the training configuration json

    Returns:
        tuple[float, float]: tuple holding the test score, prediction time metrics
    """
    config = config.__dict__
    config["dataset_configuration"] = json.loads(config["dataset_configuration"])
    file_path = config["dataset_path"]
    result_path = config["result_folder_location"]
    # predict
    os.chmod(os.path.join(result_path, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    if(config["configuration"]["task"] in [":tabular_classification", ":tabular_regression", ":text_regression", ":text_classification"]):
        train, test = data_loader(config)
        target = config["configuration"]["target"]
        # override file_path to path to test file
        file_path = write_tabular_dataset_test_data(test, os.path.dirname(file_path))
        
    elif(config["configuration"]["task"] in[":image_classification", ":image_regression"]):
        X_train, y_train, X_val, y_val, X_test, y_test = data_loader(config)

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(result_path, "predict.py"), file_path, config_path, os.path.join(result_path, "predictions.csv")])
    predict_time = time.time() - predict_start

    predictions = pd.read_csv(os.path.join(result_path, "predictions.csv"))
    os.remove(os.path.join(result_path, "predictions.csv"))

    if config["configuration"]["task"] == ":tabular_classification":
        return accuracy_score(test[target], predictions["predicted"]), (predict_time * 1000) / test.shape[0]

    elif config["configuration"]["task"] == ":tabular_regression":
        return mean_squared_error(test[target], predictions["predicted"], squared=False), \
               (predict_time * 1000) / test.shape[0]

    elif config["configuration"]["task"] == ":image_classification":
        return accuracy_score(y_test, predictions["predicted"]), (predict_time * 1000) / y_test.shape[0]

    elif config["configuration"]["task"] == ":image_regression":
        return mean_squared_error(y_test, predictions["predicted"], squared=False), \
               (predict_time * 1000) / y_test.shape[0]
    elif config["configuration"]["task"] == ":time_series_classification":
        train, test = data_loader(config)
        target = config["configuration"]["target"]

        test_target = test[target].astype("string")
        predicted_target = predictions["predicted"].astype("string")
        acc_score = accuracy_score(test_target, predicted_target)
        print("accuracy", acc_score)
        print("Classification Report \n",
              classification_report(test_target, predicted_target,zero_division=0)
              )
        return acc_score, (predict_time * 1000) / test.shape[0]

    elif config["configuration"]["task"] == ":text_classification":
        return accuracy_score(test[target], predictions["predicted"]), (predict_time * 1000) / test.shape[0]

    elif config["configuration"]["task"] == ":text_regression":
        return mean_squared_error(test[target], predictions["predicted"], squared=False), \
               (predict_time * 1000) / test.shape[0]


def predict(config: dict, config_path: str, automl: str) -> Tuple[float, str]:
    """Execute a prediction on an uploaded live dataset

    Args:
        config (dict): The prediction configuration holding the prediction request information
        config_path (str): The path to the training configuration json path
        automl (str): The AutoML adapter name, needed to find the correct path

    Returns:
        tuple[float, str]: Result tuple with the prediction time metric and the path to the prediction.csv holding the prediction made by the model
    """
    result_folder_location = os.path.join(get_config_property("training-path"),
                                        config["user_id"],
                                        config["dataset_id"],
                                        config["training_id"],
                                        get_config_property("result-folder-name"))

    #if config["task"] == ":time_series_classification":
        # Time Series Classification Task
    #    file_path = os.path.join(result_folder_location, "test.ts")
    #else:
    #    file_path = os.path.join(result_folder_location, "test.csv")

    #with open(file_path, "w+") as f:
    #    f.write(data)

    # predict
    os.chmod(os.path.join(result_folder_location, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")
    file_path = config["prediction_id"] + "_" + automl + ".csv"
    result_prediction_path = os.path.join(os.path.dirname(config["live_dataset_path"]), file_path)
    predict_start = time.time()
    subprocess.call([python_env, os.path.join(result_folder_location, "predict.py"), config["live_dataset_path"], config_path, result_prediction_path])
    predict_time = time.time() - predict_start

    
    return predict_time, result_prediction_path

def setup_run_environment(request: "StartAutoMlRequest", adapter_name: str) -> "StartAutoMlRequest":
    """Setup the necessary folder structure for the new training

    Args:
        request (StartAutoMlRequest): The training request configuration
        adapter_name (str): The adapter name

    Returns:
        StartAutoMlRequest: The extended training request configuration holding the training paths
    """

    #folder location for job related files
    job_folder_location = os.path.join(get_config_property("training-path"),
                                        request.user_id,
                                        request.dataset_id,
                                        request.training_id,
                                        get_config_property("job-folder-name"))

    #folder location for automl generated model files (not copied in ZIP)
    model_folder_location = os.path.join(get_config_property("training-path"),
                                        request.user_id,
                                        request.dataset_id,
                                        request.training_id,
                                        get_config_property("model-folder-name"))

    export_folder_location = os.path.join(get_config_property("training-path"),
                                        request.user_id,
                                        request.dataset_id,
                                        request.training_id,
                                        get_config_property("export-folder-name"))

    result_folder_location = os.path.join(get_config_property("training-path"),
                                        request.user_id,
                                        request.dataset_id,
                                        request.training_id,
                                        get_config_property("result-folder-name"))

    controller_export_folder_location  = os.path.join(get_config_property("training-path"),
                                        adapter_name,
                                        request.user_id,
                                        request.dataset_id,
                                        request.training_id,
                                        get_config_property("export-folder-name"))

    request.job_folder_location = job_folder_location
    request.model_folder_location = model_folder_location
    request.export_folder_location = export_folder_location
    request.result_folder_location = result_folder_location
    request.controller_export_folder_location = controller_export_folder_location

    #Make sure job folders exists
    os.makedirs(job_folder_location, exist_ok=True)
    os.makedirs(model_folder_location, exist_ok=True)
    os.makedirs(export_folder_location, exist_ok=True)
    os.makedirs(result_folder_location, exist_ok=True)
    request_dict = request.__dict__
    request_dict.pop("_serialized_on_wire")
    request_dict.pop("_unknown_fields")
    request_dict.pop("_group_current")
    request_dict.update({"configuration": request_dict["configuration"].__dict__})
    request_dict["configuration"].pop("_serialized_on_wire")
    request_dict["configuration"].pop("_unknown_fields")
    request_dict["configuration"].pop("_group_current")
    #Save job file
    with open(os.path.join(job_folder_location, get_config_property("job-file-name")), "w+") as f:
        json.dump(request_dict, f)
        
    return request

#endregion

######################################################################
## TABULAR DATASET HELPER FUNCTIONS
######################################################################

#region

def cast_dataframe_column(dataframe: pd.DataFrame, column_index: Any, datatype: Any) -> pd.DataFrame:
    """Cast a specific column to a new data type

    Args:
        dataframe (pd.DataFrame): The dataset dataframe
        column_index (Any): The column index which will be casted to a new data type
        datatype (Any): The new data type for the column

    Returns:
        pd.DataFrame: The new dataset dataframe with the casted column
    """
    if DataType(datatype) is DataType.DATATYPE_CATEGORY:
        dataframe[column_index] = dataframe[column_index].astype('category')
    elif DataType(datatype) is DataType.DATATYPE_BOOLEAN:
        dataframe[column_index] = dataframe[column_index].astype('bool')
    elif DataType(datatype) is DataType.DATATYPE_INT:
        dataframe[column_index] = dataframe[column_index].astype('int')
    elif DataType(datatype) is DataType.DATATYPE_FLOAT:
        dataframe[column_index] = dataframe[column_index].astype('float')
    return dataframe

def read_tabular_dataset_training_data(config: "StartAutoMlRequest") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Read a CSV dataset into train and test dataframes

    Args:
        config (StartAutoMlRequest): The extended training request configuration holding the training paths

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Dataframe tuples holding the training and test datasets tuple[(train), (test)]
    """
    delimiters = {
        "comma":        ",",
        "semicolon":    ";",
        "space":        " ",
        "tab":          "\t",
    }


    data = pd.read_csv(os.path.join(config["dataset_path"]), delimiter=delimiters[config["dataset_configuration"]['file_configuration']['delimiter']], skiprows=(config["dataset_configuration"]['file_configuration']['start_row']-1), escapechar=config["dataset_configuration"]['file_configuration']['escape_character'], decimal=config["dataset_configuration"]['file_configuration']['decimal_character'])

    # convert all object columns to categories, because autosklearn only supports numerical,
    # bool and categorical features
    #TODO: change to ontology based preprocessing
    data[data.select_dtypes(['object']).columns] = data.select_dtypes(['object']).apply(lambda x: x.astype('category'))

    # split training set
    #if SplitMethod.SPLIT_METHOD_RANDOM.value == json_configuration["test_configuration"]["method"]:
    #    train = data.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
    #    test = data.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
    #else:
    train = data.iloc[:int(data.shape[0] * 0.8)]
    test = data.iloc[int(data.shape[0] * 0.8):]

    return train, test

def write_tabular_dataset_test_data(df: pd.DataFrame, dir_name: str) -> str:
    """Writes dataframe into a csv file.

    Args:
        df (pd.DataFrame): The dataset dataframe
        dir_name (str): path of output directory

    Returns:
        file_path (str): file path to output file "test.csv"
    """
    file_path = os.path.join(dir_name, "test.csv")
    #np.reshape(df, (-1, 1))
    pd.DataFrame(data=df, columns=df.columns).to_csv(file_path, index=False)
    os.chmod(file_path, 0o744)
    return file_path


def prepare_tabular_dataset(df: pd.DataFrame, json_configuration: dict) -> Tuple[pd.DataFrame, pd.Series]:
    """Prepare tabular dataset, perform feature preparation and data type casting

    Args:
        df (pd.DataFrame): The dataset dataframe
        json_configuration (dict): the training configuration dictonary

    Returns:
        tuple[pd.DataFrame, pd.Series]: tuple holding the dataset dataframe without the target column, and a Series holding the Target column tuple[(X_dataframe, y_series)]
    """
    df = feature_preparation(df, json_configuration["dataset_configuration"]["column_datatypes"].items())
    if json_configuration["dataset_configuration"]["ignored_samples"]:
        df = df.drop(json_configuration["dataset_configuration"]["ignored_samples"])
    df = cast_dataframe_column(df, json_configuration["configuration"]["target"], json_configuration["dataset_configuration"]["column_datatypes"][json_configuration["configuration"]["target"]])
    X = df.drop(json_configuration["configuration"]["target"], axis=1)
    y = df[json_configuration["configuration"]["target"]]
    return X, y

def convert_X_and_y_dataframe_to_numpy(X: pd.DataFrame, y: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
    """Convert the X and y dataframes to numpy datatypes and fill up nans

    Args:
        X (pd.DataFrame): The dataset dataframe holding the features without target
        y (pd.Series): The dataset series holding only the target

    Returns:
        tuple[np.ndarray, np.ndarray]: Tuple holding numpy array versions of the dataset, and target variable tuple[dataset, target]
    """
    X = X.to_numpy()
    X = np.nan_to_num(X, 0)
    y = y.to_numpy()
    return X, y

#endregion

######################################################################
## IMAGE DATASET HELPER FUNCTIONS
######################################################################

#region

def read_image_dataset(config: "StartAutoMlRequest") -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read image dataset and create training and test dataframes

    Args:
        config (StartAutoMlRequest): The extended training request configuration holding the training paths

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: Dataframe tuples holding the different datasets: tuple[(X_train), (y_train), (X_test), (y_test)]
    """
    # Treat file location like URL if it does not exist as dir. URL/Filename need to be specified.
    # Mainly used for testing purposes in the hard coded json for the job
    # Example: app-data/datasets vs https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz
    """
    if not (os.path.exists(os.path.join(local_dir_path, json_configuration["file_name"]))):
        local_file_path = tf.keras.utils.get_file(
            origin=json_configuration["file_location"], 
            fname="image_data", 
            cache_dir=os.path.abspath(os.path.join("app-data")), 
            extract=True
        )

        local_dir_path = os.path.dirname(local_file_path)
    """
    data_dir = config.file_location
    train_df_list =[]
    test_df_list =[]

    def read_image_dataset_folder(sub_folder_type):
        files = []
        df = []
        for folder in os.listdir(os.path.join(data_dir, sub_folder_type)):
            files.append(glob.glob(os.path.join(data_dir, sub_folder_type, folder, "*.jpeg")))

        df_list =[]
        for i in range(len(files)):
            df = pd.DataFrame()
            df["name"] = [x for x in files[i]]
            df['outcome'] = i
            df_list.append(df)
        return df_list

    train_df_list = read_image_dataset_folder("train")
    test_df_list = read_image_dataset_folder("test")

    train_data = pd.concat(train_df_list, axis=0,ignore_index=True)
    test_data = pd.concat(test_df_list, axis=0,ignore_index=True)

    def img_preprocess(img):
        """
        Opens the image and does some preprocessing 
        such as converting to RGB, resize and converting to array
        """
        img = Image.open(img)
        img = img.convert('RGB')
        img = img.resize((256,256))
        img = np.asarray(img)/255
        return img

    X_train = np.array([img_preprocess(p) for p in train_data.name.values])
    y_train = train_data.outcome.values
    X_test = np.array([img_preprocess(p) for p in test_data.name.values])
    y_test = test_data.outcome.values
    return X_train, y_train, X_test, y_test
    
#endregion


######################################################################
## LONGITUDINAL DATASET HELPER FUNCTIONS
######################################################################

#region

def read_longitudinal_dataset(json_configuration: dict):
    """Read longitudinal data from the `.ts` file and generate training and test datasets

    Args:
        json_configuration (dict): The training configuration dictionary

    Returns:
        Any: tuple of training and test dataset
    """
    from sktime.datasets import load_from_tsfile_to_dataframe

    file_path = os.path.join(json_configuration["file_location"], json_configuration["file_name"])
    dataset = load_from_tsfile_to_dataframe(file_path, return_separate_X_and_y=False)
    dataset = dataset.rename(columns={"class_vals": "target"})
    return split_dataset(dataset, json_configuration)


def split_dataset(dataset: Any, json_configuration: dict):
    """Split the given dataset into train and test subsets

    Args:
        dataset (Any): The loaded TS dataset
        json_configuration (dict): The training configuration dictionary

    Returns:
        _type_: tuple of training and test dataset
    """
    
    split_method = json_configuration["test_configuration"]["method"]
    split_ratio = json_configuration["test_configuration"]["split_ratio"]
    random_state = json_configuration["test_configuration"]["random_state"]
    np.random.seed(random_state)

    if int(SplitMethod.SPLIT_METHOD_RANDOM.value) == split_method:
        return train_test_split(
            dataset,
            train_size=split_ratio,
            random_state=random_state,
            shuffle=True,
            stratify=dataset["target"]
        )
    else:
        return train_test_split(
            dataset,
            train_size=split_ratio,
            shuffle=False,
            stratify=dataset["target"]
        )
#endregion
