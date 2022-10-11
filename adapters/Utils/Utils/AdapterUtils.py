from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
import json
import os
import shutil
import subprocess
import sys
import time, datetime
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

######################################################################
## GRPC HELPER FUNCTIONS
######################################################################

#region

def get_except_response(e):
    """
    Get exception message
    ---
    Parameter
    1. exception
    ---
    Return exception GRPC message
    """
    print(e)
    response = GetAutoMlStatusResponse()
    response.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_ERROR
    return response


def capture_process_output(process, start_time , use_error):
    """
    Read console log from subprocess, and send it after each \n to the controller
    ---
    Parameter
    1. system process representing the AutoML process
    2. Process start time
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
            process_update.output_json = ""
            process_update.runtime = int(time.time() - start_time) or 0
            # if return Code is ADAPTER_RETURN_CODE_STATUS_UPDATE we do not have score values yet
            process_update.test_score = 0.0
            process_update.prediction_time = 0.0
            process_update.library = ""
            process_update.model = ""
            yield process_update

            sys.stdout.write(capture)
            sys.stdout.flush()
            capture = ""
        if(use_error == False):
            s = process.stdout.read(1)
        else:
            s = process.stderr.read(1)
        capture += s


def get_response(output_json, start_time, test_score, prediction_time, library, model):
    """
    Get Start automl response object
    ---
    Parameter
    1. output json
    2. process start time
    3. test score of the new model
    4. prediction time
    5. used ML library
    6. model object
    ---
    Return the process result message
    """
    response = GetAutoMlStatusResponse()
    response.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_SUCCESS
    response.path = os.path.join(output_json.file_location, output_json.file_name)
    response.test_score = test_score
    response.prediction_time = prediction_time
    response.library = library
    response.model = model
    return response


#endregion

######################################################################
## GENERAL HELPER FUNCTIONS
######################################################################

#region

def data_loader(config):
    """
    Get exception message
    ---
    Parameter
    1. config: Job config
    ---
    Return job type specific dataset
    """

    train_data = None
    test_data = None

    if config["configuration"]["task"] in [":tabular_classification", ":tabular_regression", ":text_classification", ":time_series_forecasting", ":time_series_classification"]:
        return read_tabular_dataset_training_data(config)
    elif config["configuration"]["task"] in [":image_classification", ":image_regression"]:
        return read_image_dataset(config)
    return train_data, test_data


def export_model(model, path, file_name):
    """
    Export the generated ML model to disk
    ---
    Parameter:
    1. generate ML model
    """
    with open(os.path.join(path, file_name), 'wb+') as file:
        dill.dump(model, file)


def start_automl_process(config):
    """"
    @:return started automl process
    """
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    return subprocess.Popen([python_env, "AutoML.py", config.job_folder_location],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)

def generate_script(config):
    """
    Generate the result python script
    ---
    Parameter
    1. process configuration
    """
    generator = TemplateGenerator(config)
    generator.generate_script()

def zip_script(config):
    """
    Zip the model and script from the current run
    ---
    Parameter
    1. current run training id
    ---
    Return json with zip information
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

def evaluate(config, config_path, dataloader):
    """
    Evaluate the model by using the test set
    ---
    Parameter
    1. configuration json
    2. configuration path
    3. dataloader
    ---
    Return evaluation score
    """
    config = config.__dict__
    config["dataset_configuration"] = json.loads(config["dataset_configuration"])
    file_path = config["dataset_path"]
    result_path = config["result_folder_location"]
    # predict
    os.chmod(os.path.join(result_path, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(result_path, "predict.py"), file_path, config_path, os.path.join(result_path, "predictions.csv")])
    predict_time = time.time() - predict_start

    if(config["configuration"]["task"] in [":tabular_classification", ":tabular_regression", ":text_regression", ":text_classification"]):
        train, test = data_loader(config)
        target = config["configuration"]["target"]
    elif(config["configuration"]["task"] in[":image_classification", ":image_regression"]):
        X_train, y_train, X_val, y_val, X_test, y_test = data_loader(config)

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


def predict(config_json, config_path, automl):
    """
    Make a prediction on test data
    ---
    Parameter
    1. prediction data
    2. configuration json
    3. configuration path
    ---
    Return prediction score 
    """
    result_folder_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_id"],
                                        config_json["dataset_id"],
                                        config_json["training_id"],
                                        get_config_property("result-folder-name"))

    #if config_json["task"] == ":time_series_classification":
        # Time Series Classification Task
    #    file_path = os.path.join(result_folder_location, "test.ts")
    #else:
    #    file_path = os.path.join(result_folder_location, "test.csv")

    #with open(file_path, "w+") as f:
    #    f.write(data)

    # predict
    os.chmod(os.path.join(result_folder_location, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")
    file_path = config_json["prediction_id"] + "_" + automl + ".csv"
    result_prediction_path = os.path.join(os.path.dirname(config_json["live_dataset_path"]), file_path)
    predict_start = time.time()
    subprocess.call([python_env, os.path.join(result_folder_location, "predict.py"), config_json["live_dataset_path"], config_path, result_prediction_path])
    predict_time = time.time() - predict_start

    
    return predict_time, result_prediction_path

def SetupRunNewRunEnvironment(request: "StartAutoMlRequest"):

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

    request.job_folder_location = job_folder_location
    request.model_folder_location = model_folder_location
    request.export_folder_location = export_folder_location
    request.result_folder_location = result_folder_location

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

def cast_dataframe_column(dataframe, column_index, datatype):
    """
    Cast a specific column to a new data type
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

def read_tabular_dataset_training_data(config):
    """
    Read the training dataset from disk
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
    test = data.iloc[int(data.shape[0] * 0.2):]

    return train, test

def prepare_tabular_dataset(df, json_configuration):
    """
    Prepare tabular dataset, perform feature preparation and data type casting
    """
    df = feature_preparation(df, json_configuration["dataset_configuration"]["column_datatypes"].items())
    df = cast_dataframe_column(df, json_configuration["configuration"]["target"], json_configuration["dataset_configuration"]["column_datatypes"][json_configuration["configuration"]["target"]])
    X = df.drop(json_configuration["configuration"]["target"], axis=1)
    y = df[json_configuration["configuration"]["target"]]
    return X, y

def convert_X_and_y_dataframe_to_numpy(X, y):
    """
    Convert the X and y dataframes to numpy datatypes and fill up nans
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

def read_image_dataset(config):
    """Reads image data and creates AutoKeras specific structure/sets
    ---
    Parameter
    1. config: Job config
    ---
    Return image dataset
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

def read_longitudinal_dataset(json_configuration):
    """
    Read longitudinal data from the `.ts` file
    """
    from sktime.datasets import load_from_tsfile_to_dataframe

    file_path = os.path.join(json_configuration["file_location"], json_configuration["file_name"])
    dataset = load_from_tsfile_to_dataframe(file_path, return_separate_X_and_y=False)
    dataset = dataset.rename(columns={"class_vals": "target"})
    return split_dataset(dataset, json_configuration)


def split_dataset(dataset, json_configuration):
    """
    Split the given dataset into train and test subsets
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
