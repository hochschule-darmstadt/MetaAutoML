from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
import json
import os
import shutil
import subprocess
import time
from typing import Any
import dill
import pandas as pd
from sklearn.metrics import *
from JsonUtil import get_config_property
from TemplateGenerator import TemplateGenerator
from AdapterBGRPC import *
from typing import Tuple
import re
from AdapterImageUtils import *
from AdapterLongitudinalUtils import *
from AdapterTabularUtils import *


def read_parameter(parameters, intersect_parameter, automl_parameter, default=[None]):
    """Checks if the intersected parameter or if the individual parameter is set

    Args:
        parameters (_type_): all parameters from the config
        intersect_parameter (_type_): common parameter name (broader id)
        automl_parameter (_type_): individual parameter for the automl
        default (list, optional): Default value if none of the above is set. Defaults to [None].

    Returns:
        _type_: Returns all parameter values that are selected (intersected + individual), if none the default value is taken
    """
    value = list()
    try:
        value = parameters[intersect_parameter]['values']
    except:
        pass
    try:
        values2 = parameters[automl_parameter]['values']
        for para in values2:
            if para not in value:
                value.append(para)
    except:
        pass
    if len(value) == 0:
        return default
    else:
        return value
        
def translate_parameters(task, parameter, task_config):
    """_summary_

    Args:
        task (_type_): AutoML task (e.g tabular_classification)
        parameter (_type_): List of all selected parameters
        task_config (_type_): config for all tasks. includes the translation to the autoML specific types and values

    Returns:
        _type_: returns a dictionary. The key is given by the task config. The values are set with the read_parameters function
    """
    final_dict = {}
    final_value = None
    for para in task_config[task]:
        values = read_parameter(parameter, para[0], para[1], para[2])
        if para[3] == "list":
            final_value = list()
            for value in values:
                if para[4] == "dict":
                    translateList = para[5]
                    final_value.append(translateList.get(value, None))
                elif para[4] == "integer":
                    final_value.append(int(value))
        else:
            if para[4] == "dict":
                if values[0] == None:
                    final_value = None
                else:
                    final_value = para[5][values[-1]]
            elif para[4] == "integer":
                if values[0] == None:
                    final_value = None
                else:
                    final_value = int(values[len(values) - 1])
        final_dict.update({ para[6]: final_value})

    return final_dict



def data_loader(config: "StartAutoMlRequest", image_test_folder=False, perform_splitting=True, as_dataframe=False) -> Any:
    """Load the dataframes for the requested dataset, by loading them into different DataFrames. See Returns section for more information.

    Args:
        config (StartAutoMlRequest): The StartAutoMlRequest request, extended with the trainings folder paths
        image_test_folder (Boolean): Used for image datasets, if the test folder should be loaded. Default is, read the train folder

    Returns:
        Any: Depending on the dataset type: CSV data: tuple[DataFrame (Train), DataFrame (Test)], image data: tuple[DataFrame (X_train), DataFrame (y_train), DataFrame (X_test), DataFrame (y_test)]
    """

    if config["configuration"]["task"] in [":image_classification", ":image_regression"]:
        return read_image_dataset(config, image_test_folder, as_dataframe)
    else:
        return read_tabular_dataset_training_data(config, perform_splitting)


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
    index = []
    for key in config["dataset_configuration"]["schema"]:
        #Get target columns list
        if config["dataset_configuration"]["schema"][key].get("role_selected", "") == ":target":
            targets.append(key)
        if config["dataset_configuration"]["schema"][key].get("role_selected", "") == ":index":
            index.append(key)

    if(config["configuration"]["task"] in [":tabular_classification", ":tabular_regression", ":text_regression", ":text_classification"]):
        train, test = data_loader(config)
        target = targets[0]
        # override file_path to path to test file and drop target column
        file_path = write_tabular_dataset_data(test.drop(target, axis=1), os.path.dirname(file_path), config)

    elif(config["configuration"]["task"] in[":time_series_forecasting"]):
        train, test = data_loader(config)
        target = targets[0]
        # override file_path to path to test file and drop target column
        #TODO must set dynamic future prediction length

        #y_actual = test.iloc[-12:][target]
        #test.drop(test.tail(12).index, inplace=True)
        file_path = write_tabular_dataset_data(test, os.path.dirname(file_path), config)

    elif(config["configuration"]["task"] in[":image_classification", ":image_regression"]):
        X_test, y_test = data_loader(config, image_test_folder=True)

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(result_path, "predict.py"), file_path, os.path.join(result_path, "predictions.csv")])
    predict_time = time.time() - predict_start

    predictions = pd.read_csv(os.path.join(result_path, "predictions.csv"))
    os.remove(os.path.join(result_path, "predictions.csv"))

    if config["configuration"]["task"] in [":tabular_classification", ":text_classification", ":image_classification", ":time_series_classification"]:
        if config["configuration"]["task"] == ":image_classification":
            return compute_classification_metrics(pd.Series(y_test), predictions["predicted"]), (predict_time * 1000) / pd.Series(y_test).shape[0]
        else:
            return compute_classification_metrics(pd.Series(test[target]), predictions["predicted"]), (predict_time * 1000) / test.shape[0]
    elif config["configuration"]["task"] in [":tabular_regression", ":text_regression", ":image_regression", ":time_series_forecasting"]:
        if config["configuration"]["task"] == ":image_regression":
            return compute_regression_metrics(pd.Series(y_test), predictions["predicted"]), (predict_time * 1000) / pd.Series(y_test).shape[0]
        elif config["configuration"]["task"] == ":time_series_forecasting":
            #TODO add dynamic future prediction
            return compute_regression_metrics(pd.Series(test.iloc[-12:][target]), predictions["predicted"]), (predict_time * 1000) / test.shape[0]
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
        labels = [value for value in y_should.unique() if value not in y_is.unique()]
        labels = np.append(y_is.unique(), labels)
        enc.fit(labels)
        y_should = pd.Series(enc.transform(y_should))
        y_is = pd.Series(enc.transform(y_is))
    score = {
        ":accuracy": float(accuracy_score(y_should, y_is)),
        ":balanced_accuracy": float(balanced_accuracy_score(y_should, y_is)),
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
        ":recall": float(recall_score(y_should, y_is)),
        ":brier": float(brier_score_loss(y_should, y_is)),
        })
    else:
        #Metrics only for multiclass classification
        score.update({

        ":f_measure_micro": float(f1_score(y_should, y_is, average='micro')),
        ":f_measure_macro": float(f1_score(y_should, y_is, average='macro')),
        ":f_measure_weighted": float(f1_score(y_should, y_is, average='weighted')),
        ":precision_micro": float(precision_score(y_should, y_is, average='micro')),
        ":precision_macro": float(precision_score(y_should, y_is, average='macro')),
        ":precision_weighted": float(precision_score(y_should, y_is, average='weighted')),
        ":recall_micro": float(recall_score(y_should, y_is, average='micro')),
        ":recall_macro": float(recall_score(y_should, y_is, average='macro')),
        ":recall_weighted": float(recall_score(y_should, y_is, average='weighted')),
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
        ":d2_tweedie_score": float(d2_tweedie_score(y_should, y_is)),
        ":mean_squared_log_error": float(mean_squared_log_error(y_should, y_is, squared=True)),
        ":rooted_mean_squared_log_error": float(mean_squared_log_error(y_should, y_is, squared=False))
        })
    except Exception as e:
        print("computing D2 scores failed")
    if all(val > 0 for val in y_is) and all(val > 0 for val in y_should):
        score.update({
        ":mean_poisson_deviance": float(mean_poisson_deviance(y_should, y_is)),
        ":mean_gamma_deviance": float(mean_gamma_deviance(y_should, y_is))
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
            request_dict["dataset_path"] = re.sub("[a-zA-Z]:\\\\([A-Za-z0-9_]+(\\\\[A-Za-z0-9_]+)+)\\\\MetaAutoML", get_config_property("wsl_metaautoml_path"), request_dict["dataset_path"])
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
