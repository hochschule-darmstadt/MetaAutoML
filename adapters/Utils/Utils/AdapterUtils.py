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
from predict_time_sources import SplitMethod, feature_preparation
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.metrics import *
from sklearn.metrics import mean_absolute_percentage_error
from JsonUtil import get_config_property
from TemplateGenerator import TemplateGenerator
import glob
from PIL import Image
from AdapterBGRPC import *
from typing import Tuple
import re
from codecarbon.output import EmissionsData
import random
######################################################################
## GRPC HELPER FUNCTIONS
######################################################################

#region

def get_response(config: "StartAutoMlRequest", test_score: float, prediction_time: float, library: str, model: str, emissions: EmissionsData) -> "GetAutoMlStatusResponse":
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

    #Add emission profile
    emission_profile = CarbonEmission()
    emission_profile.emissions = emissions.emissions
    emission_profile.emissions_rate = emissions.emissions_rate
    emission_profile.energy_consumed = emissions.energy_consumed
    emission_profile.duration = emissions.duration
    emission_profile.cpu_count = emissions.cpu_count
    emission_profile.cpu_energy = emissions.cpu_energy
    emission_profile.cpu_model = emissions.cpu_model
    emission_profile.cpu_power = emissions.cpu_power
    emission_profile.gpu_count = emissions.gpu_count
    emission_profile.gpu_energy = emissions.gpu_energy
    emission_profile.gpu_model = emissions.gpu_model
    emission_profile.gpu_power = emissions.gpu_power
    emission_profile.ram_energy = emissions.ram_energy
    emission_profile.ram_power = emissions.ram_power
    emission_profile.ram_total_size = emissions.ram_total_size

    response.emission_profile = emission_profile
    return response


#endregion

######################################################################
## GENERAL HELPER FUNCTIONS
######################################################################

#region

def data_loader(config: "StartAutoMlRequest", image_test_folder=False) -> Any:
    """Load the dataframes for the requested dataset, by loading them into different DataFrames. See Returns section for more information.

    Args:
        config (StartAutoMlRequest): The StartAutoMlRequest request, extended with the trainings folder paths
        image_test_folder (Boolean): Used for image datasets, if the test folder should be loaded. Default is, read the train folder

    Returns:
        Any: Depending on the dataset type: CSV data: tuple[DataFrame (Train), DataFrame (Test)], image data: tuple[DataFrame (X_train), DataFrame (y_train), DataFrame (X_test), DataFrame (y_test)]
    """

    if config["configuration"]["task"] in [":image_classification", ":image_regression"]:
        return read_image_dataset(config, image_test_folder)
    else:
        return read_tabular_dataset_training_data(config)


def export_model(model: Any, path: str, file_name: str):
    """Export a model instance to disc by using dill

    Args:
        model (Any): The AutoML solutions model instance
        path (str): The absolute folder path where to save the model to
        file_name (str): The file name for the saved model
    """
    with open(os.path.join(path, file_name), 'wb+') as file:
        dill.dump(model, file)

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
    #shutil.copy(get_config_property("predict-time-sources-path"),
    #            result_path)

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
    config["dataset_configuration"] = config["dataset_configuration"]
    file_path = config["dataset_path"]
    if config["configuration"]["task"] in[":image_classification", ":image_regression"]:
        #for image data we need to redirect to the test folder
        file_path = os.path.join(file_path, "test")
    result_path = config["result_folder_location"]
    # predict
    os.chmod(os.path.join(result_path, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")
    targets = []
    for key in config["dataset_configuration"]["schema"]:
        #Get target columns list
        if config["dataset_configuration"]["schema"][key].get("role_selected", "") == ":target":
            targets.append(key)

    if(config["configuration"]["task"] in [":tabular_classification", ":tabular_regression", ":text_regression", ":text_classification", ":time_series_forecasting"]):
        train, test = data_loader(config)
        target = targets[0]
        # override file_path to path to test file and drop target column
        file_path = write_tabular_dataset_data(test.drop(target, axis=1), os.path.dirname(file_path), config)

    elif(config["configuration"]["task"] in[":image_classification", ":image_regression"]):
        X_test, y_test = data_loader(config, image_test_folder=True)

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(result_path, "predict.py"), file_path, os.path.join(result_path, "predictions.csv")])
    predict_time = time.time() - predict_start

    predictions = pd.read_csv(os.path.join(result_path, "predictions.csv"))
    os.remove(os.path.join(result_path, "predictions.csv"))

    if config["configuration"]["task"] in [":tabular_classification", ":text_classification", ":image_classification", ":time_series_classification"]:
        if config["configuration"]["task"] == ":image_classification":
            return compute_classification_metrics(y_test, predictions["predicted"]), (predict_time * 1000) / pd.Series(y_test).shape[0]
        else:
            return compute_classification_metrics(pd.Series(test[target]), predictions["predicted"]), (predict_time * 1000) / test.shape[0]
    elif config["configuration"]["task"] in [":tabular_regression", ":text_regression", ":image_regression", ":time_series_forecasting"]:
        if config["configuration"]["task"] == ":image_regression":
            return compute_regression_metrics(y_test, predictions["predicted"]), (predict_time * 1000) / pd.Series(y_test).shape[0]
        else:
            return compute_regression_metrics(pd.Series(test[target]), predictions["predicted"]), (predict_time * 1000) / test.shape[0]

def compute_classification_metrics(y_should: pd.Series, y_is: pd.Series) -> dict:
    """Compute the metrics collection for classification tasks

    Args:
        y_should (pd.Series): The series of the label for the test set
        y_is (pd.Series): The series of the label of the model predictions for the test set

    Returns:
        dict: Dictionary containing the computed metrics, key is ontology IRI for the metric and value is the value
    """
    from sklearn.preprocessing import LabelEncoder

    if y_is.dtype == object:
        #If the label is string based, we need to convert it to int values or else some metric wont compute correctly
        enc = LabelEncoder()
        enc.fit(y_should.unique())
        y_should = pd.Series(enc.transform(y_should))
        y_is = pd.Series(enc.transform(y_is))
    score = {
        ":accuracy": float(accuracy_score(y_should, y_is)),
        ":balanced_accuracy": float(balanced_accuracy_score(y_should, y_is)),
        ":brier": float(brier_score_loss(y_should, y_is)),
    }
    if len(y_should.unique()) == 2:
        #Metrics only for binary classification
        tn, fp, fn, tp = confusion_matrix(y_should, y_is).ravel()
        score.update({
        ":average_precision": float(average_precision_score(y_should, y_is, average='weighted')),
        ":true_positives": float(tp),
        ":false_positives": float(fp),
        ":true_negatives": float(tn),
        ":false_negatives": float(fn),
        ":f_measure": float(f1_score(y_should, y_is)),
        ":precision": float(precision_score(y_should, y_is)),
        ":recall": float(recall_score(y_should, y_is))
        })
    else:
        #Metrics only for multiclass classification
        score.update({

        ":f_measure": float(f1_score(y_should, y_is, average=None)),
        ":f_measure_micro": float(f1_score(y_should, y_is, average='micro')),
        ":f_measure_macro": float(f1_score(y_should, y_is, average='macro')),
        ":f_measure_weighted": float(f1_score(y_should, y_is, average='weighted')),
        ":precision": float(precision_score(y_should, y_is, average=None)),
        ":precision_micro": float(precision_score(y_should, y_is, average='micro')),
        ":precision_macro": float(precision_score(y_should, y_is, average='macro')),
        ":precision_weighted": float(precision_score(y_should, y_is, average='weighted')),
        ":recall": float(recall_score(y_should, y_is, average=None)),
        ":recall_micro": float(recall_score(y_should, y_is, average='micro')),
        ":recall_macro": float(recall_score(y_should, y_is, average='macro')),
        ":recall_weighted": float(recall_score(y_should, y_is, average='weighted'))
        })
    return score

def compute_regression_metrics(y_should: pd.Series, y_is: pd.Series) -> dict:
    """Compute the metrics collection for regression tasks

    Args:
        y_should (pd.Series): The series of the label for the test set
        y_is (pd.Series): The series of the label of the model predictions for the test set

    Returns:
        dict: Dictionary containing the computed metrics, key is ontology IRI for the metric and value is the value
    """
    score = {
        ":explained_variance": float(explained_variance_score(y_should, y_is)),
        ":max_error": float(max_error(y_should, y_is)),
        ":mean_absolute_error": float(mean_absolute_error(y_should, y_is)),
        ":mean_squared_error": float(mean_squared_error(y_should, y_is, squared=True)),
        ":rooted_mean_squared_error": float(mean_squared_error(y_should, y_is, squared=False)),
        ":median_absolute_error": float(median_absolute_error(y_should, y_is)),
        ":r2": float(r2_score(y_should, y_is)),
        ":mean_absolute_percentage_error": float(mean_absolute_percentage_error(y_should, y_is)),
    }
    try:
        score.update({
        ":d2_absolute_error": float(d2_absolute_error_score(y_should, y_is)),
        ":d2_pinball_score": float(d2_pinball_score(y_should, y_is)),
        ":d2_tweedie_score": float(d2_tweedie_score(y_should, y_is))
        })
    except Exception as e:
        print("computing D2 scores failed:" + e)
    if all(val > 0 for val in y_is) and all(val > 0 for val in y_should):
        score.update({
        ":mean_poisson_deviance": float(mean_poisson_deviance(y_should, y_is)),
        ":mean_gamma_deviance": float(mean_gamma_deviance(y_should, y_is)),
        ":mean_squared_log_error": float(mean_squared_log_error(y_should, y_is, squared=True)),
        ":rooted_mean_squared_log_error": float(mean_squared_log_error(y_should, y_is, squared=False))
        })
    return score

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
    subprocess.call([python_env, os.path.join(result_folder_location, "predict.py"), config["live_dataset_path"], result_prediction_path])
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

    request_dict = request.to_dict(casing=betterproto.Casing.SNAKE)
    #For WSL users we need to adjust the path prefix for the dataset location to windows path
    if get_config_property("local_execution") == "YES":
        if get_config_property("running_in_wsl") == "YES":
            request_dict["dataset_path"] = re.sub("[a-zA-Z]:\\\\([A-Za-z0-9]+(\\\\[A-Za-z0-9]+)+)\\\\MetaAutoML", get_config_property("wsl_metaautoml_path"), request_dict["dataset_path"])
            request_dict["dataset_path"] = request_dict["dataset_path"].replace("\\", "/")
            job_folder_location = job_folder_location.replace("\\", "/")
            model_folder_location = model_folder_location.replace("\\", "/")
            export_folder_location = export_folder_location.replace("\\", "/")
            result_folder_location = result_folder_location.replace("\\", "/")
            controller_export_folder_location = controller_export_folder_location.replace("\\", "/")

    request_dict["job_folder_location"] = job_folder_location
    request_dict["model_folder_location"] = model_folder_location
    request_dict["export_folder_location"] = export_folder_location
    request_dict["result_folder_location"] = result_folder_location
    request_dict["controller_export_folder_location"] = controller_export_folder_location

    # TODO: Refactor AdapterManager and AdapterUtils to not rely on a proto object that some fields have been added to at runtime
    # also add values to request object (the values are used in subsequent requests)
    request.dataset_path = request_dict["dataset_path"]
    request.job_folder_location = request_dict["job_folder_location"]
    request.model_folder_location = model_folder_location
    request.export_folder_location = export_folder_location
    request.result_folder_location = result_folder_location
    request.controller_export_folder_location = controller_export_folder_location

    # TODO: Remove this and fix all places that access the configuration object as a dictionary
    # replace configuration object with dictionary
    request.configuration = request_dict["configuration"]

    #Make sure job folders exists
    os.makedirs(job_folder_location, exist_ok=True)
    os.makedirs(model_folder_location, exist_ok=True)
    os.makedirs(export_folder_location, exist_ok=True)
    os.makedirs(result_folder_location, exist_ok=True)
    #Save job file
    with open(os.path.join(job_folder_location, get_config_property("job-file-name")), "w+") as f:
        json.dump(request_dict, f)
    return request

#endregion

######################################################################
## TABULAR DATASET HELPER FUNCTIONS
######################################################################

#region

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

    configuration = {
        "filepath_or_buffer": os.path.join(config["dataset_path"]),
        "delimiter": delimiters[config['dataset_configuration']['file_configuration']['delimiter']],
        "skiprows": (config['dataset_configuration']['file_configuration']['start_row']-1),
        "decimal": config['dataset_configuration']['file_configuration']['decimal_character'],
        "escapechar": config['dataset_configuration']['file_configuration']['escape_character'],
        "encoding": config['dataset_configuration']['file_configuration']['encoding'],
    }
    if config['dataset_configuration']['file_configuration']['thousands_seperator'] != "":
        configuration["thousands"] = config['dataset_configuration']['file_configuration']['thousands_seperator']


    data = pd.read_csv(**configuration)

    if config['dataset_configuration']['multi_fidelity_level'] != 0:
        data = data.sample(frac=0.1, random_state=1)

    #Rename untitled columns to correct name
    for column in data:
        if re.match(r"Unnamed: [0-9]+", column):
            data.rename(columns={column: f"Column{data.columns.get_loc(column)}"}, inplace=True)

    # convert all object columns to categories, because autosklearn only supports numerical,
    # bool and categorical features
    #TODO: change to ontology based preprocessing
    #data[data.select_dtypes(['object']).columns] = data.select_dtypes(['object']).apply(lambda x: x.astype('category'))

    # split training set
    #if SplitMethod.SPLIT_METHOD_RANDOM.value == json_configuration["test_configuration"]["method"]:
    #    train = data.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
    #    test = data.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
    #else:
    train = data.iloc[:int(data.shape[0] * 0.8)]
    test = data.iloc[int(data.shape[0] * 0.8):]

    return train, test

def write_tabular_dataset_data(df: pd.DataFrame, dir_name: str, config, file_name: str = "test.csv") -> str:
    """Writes dataframe into a csv file.

    Args:
        df (pd.DataFrame): The dataset dataframe
        dir_name (str): path of output directory
        config (dict): the adapter process configuration
        file_name (str): file name

    Returns:
        file_path (str): file path to output file "test.csv"
    """
    delimiters = {
        "comma":        ",",
        "semicolon":    ";",
        "space":        " ",
        "tab":          "\t",
    }

    file_path = os.path.join(dir_name, file_name)
    configuration = {
        "path_or_buf": file_path,
        "sep": delimiters[config["dataset_configuration"]["file_configuration"]['delimiter']],
        "decimal": config["dataset_configuration"]["file_configuration"]['decimal_character'],
        "escapechar": config["dataset_configuration"]["file_configuration"]['escape_character'],
        "encoding": config["dataset_configuration"]["file_configuration"]['encoding'],
        "date_format": config["dataset_configuration"]["file_configuration"]["datetime_format"],
        "index": False
    }

    #np.reshape(df, (-1, 1))
    pd.DataFrame(data=df, columns=df.columns).to_csv(**configuration)
    os.chmod(file_path, 0o744)
    return file_path


def prepare_tabular_dataset(df: pd.DataFrame, json_configuration: dict) -> Tuple[pd.DataFrame, pd.Series]:
    """Prepare tabular dataset, perform feature preparation and data type casting

    Args:
        df (pd.DataFrame): The dataset dataframe
        json_configuration (dict): the training configuration dictonary

    Returns:
        tuple[pd.DataFrame, object]: tuple holding the dataset dataframe without the target column, and a Series or Dataframe holding the Target column(s) tuple[(X_dataframe, y)]
    """
    X, y = feature_preparation(df, json_configuration["dataset_configuration"]["schema"].items(), json_configuration["dataset_configuration"]["file_configuration"]["datetime_format"])
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

def get_column_with_largest_amout_of_text(X: pd.DataFrame, configuration: dict) -> Tuple[pd.DataFrame, dict]:
    """
    Find the column with the most text inside,
    because some adapters only supports training with one feature
    Args:
        X (pd.DataFrame): The current X Dataframe
        configuration (dict): hold the current adapter process configuration

    Returns:
        Tuple(pd.DataFrame, dict): pd.Dataframe: Returns a pandas Dataframe with the column with the most text inside, the dict is the updated configuraiton dict
    """
    column_names = []
    target = ""
    dict_with_string_length = {}

    #First get only columns that will be used during training
    for column, dt in configuration["dataset_configuration"]["schema"].items():
        if dt.get("role_selected", "") == ":ignore" or dt.get("role_selected", "") == ":index" or dt.get("role_selected", "") == ":target":
            continue
        column_names.append(column)

    #Check the used columns by dtype object (== string type) and get mean len to get column with longest text
    for column_name in column_names:
        if(X.dtypes[column_name] == object):
            newlength = X[column_name].str.len().mean()
            dict_with_string_length[column_name] = newlength
    max_value = max(dict_with_string_length, key=dict_with_string_length.get)

    #Remove the to be used text column from the list of used columns and set role ignore as Autokeras can only use one input column for text tasks
    column_names.remove(max_value)
    for column_name in column_names:
        configuration["dataset_configuration"]["schema"][column_name]["role_selected"] = ":ignore"

    save_configuration_in_json(configuration)
    return X, configuration


def save_configuration_in_json(configuration: dict):
    """
    serialize dataset_configuration to json string and save the the complete configuration in json file
    to habe the right datatypes available for the evaluation
    Args:
        configuration (dict): The current adapter process configuration
    """
    configuration['dataset_configuration'] = json.dumps(configuration['dataset_configuration'])
    with open(os.path.join(configuration['job_folder_location'], get_config_property("job-file-name")), "w+") as f:
        json.dump(configuration, f)
    configuration["dataset_configuration"] = json.loads(configuration["dataset_configuration"])


#endregion

######################################################################
## IMAGE DATASET HELPER FUNCTIONS
######################################################################

#region

def read_image_dataset(config: "StartAutoMlRequest", image_test_folder=False) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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

    #we need to access the train sub folder for training
    data_dir = config["dataset_path"]
    if image_test_folder == True:
        data_dir = os.path.join(data_dir, "test")
    else:
        data_dir = os.path.join(data_dir, "train")
    train_df_list =[]

    def read_image_dataset_folder():
        files = []
        df = []
        for folder in os.listdir(os.path.join(data_dir)):
            files.append(glob.glob(os.path.join(data_dir, folder, "*.jp*g")))

        df_list =[]

        if config['dataset_configuration']['multi_fidelity_level'] != 0:
            df_list = random.choices(df_list, k=int(len(files)*0.1))

        for i in range(len(files)):
            df = pd.DataFrame()
            df["name"] = [x for x in files[i]]
            df['outcome'] = i
            df_list.append(df)
        return df_list

    train_df_list = read_image_dataset_folder()

    train_data = pd.concat(train_df_list, axis=0,ignore_index=True)

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
    return X_train, y_train

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
