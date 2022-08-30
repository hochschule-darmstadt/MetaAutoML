import json
import os
import shutil
import subprocess
import sys
import time
#import autokeras as ak
#import tensorflow as tf

import Adapter_pb2
import Adapter_pb2_grpc
import dill
import grpc
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

######################################################################
## GRPC HELPER FUNCTIONS
######################################################################

#region

def get_except_response(context, e):
    """
    Get exception message
    ---
    Parameter
    1. exception
    ---
    Return exception GRPC message
    """
    print(e)
    adapter_name = get_config_property("adapter-name")
    context.set_details(f"Error while executing {adapter_name}: {e}")
    context.set_code(grpc.StatusCode.UNAVAILABLE)
    return Adapter_pb2.StartAutoMLResponse()


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
            process_update = Adapter_pb2.StartAutoMLResponse()
            process_update.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_STATUS_UPDATE
            process_update.statusUpdate = capture
            process_update.outputJson = ""
            process_update.runtime = int(time.time() - start_time) or 0
            # if return Code is ADAPTER_RETURN_CODE_STATUS_UPDATE we do not have score values yet
            process_update.testScore = 0.0
            process_update.validationScore = 0.0
            process_update.predictiontime = 0.0
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
    response = Adapter_pb2.StartAutoMLResponse()
    response.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS
    response.outputJson = json.dumps(output_json)
    response.runtime = int(time.time() - start_time)
    response.testScore = test_score
    response.validationScore = 0.0
    response.predictiontime = prediction_time
    response.library = library
    response.model = model
    yield response


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

    if config["task"] == ":tabular_classification":
        return read_tabular_dataset_training_data(config)
    elif config["task"] == ":tabular_regression":
        return read_tabular_dataset_training_data(config)
    elif config["task"] == ":image_classification":
        return read_image_dataset(config)
    elif config["task"] == ":image_regression":
        return read_image_dataset(config)
    elif config["task"] == ":text_classification":
        return read_tabular_dataset_training_data(config)
    elif config["task"] == ":time_series_forecasting":
        return read_tabular_dataset_training_data(config)
    elif config["task"] == ":time_series_classification":
        return read_longitudinal_dataset(config)

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

    return subprocess.Popen([python_env, "AutoML.py", config["user_identifier"], config["training_id"]],
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
    output_path = config["export_folder_location"]
    result_path = config["result_folder_location"]
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
                                        config["user_identifier"],
                                        config["training_id"])

    return {
        'file_name': f'{zip_file_name}.zip',
        'file_location': file_loc_on_controller
    }

def evaluate(config_json, config_path, dataloader):
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
    file_path = os.path.join(config_json["file_location"], config_json["file_name"])
    result_path = config_json["result_folder_location"]
    # predict
    os.chmod(os.path.join(result_path, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(result_path, "predict.py"), file_path, config_path])
    predict_time = time.time() - predict_start

    if(config_json["task"] == ":tabular_classification" or config_json["task"] == ":tabular_regression"):
        train, test = dataloader(config_json)
        target = config_json["configuration"]["target"]["target"]
    elif(config_json["task"] == ":image_classification" or config_json["task"] == ":image_regression"):
        X_train, y_train, X_val, y_val, X_test, y_test = data_loader(config_json)

    predictions = pd.read_csv(os.path.join(result_path, "predictions.csv"))
    os.remove(os.path.join(result_path, "predictions.csv"))

    if config_json["task"] == ":tabular_classification":
        return accuracy_score(test[target], predictions["predicted"]), (predict_time * 1000) / test.shape[0]

    elif config_json["task"] == ":tabular_regression":
        return mean_squared_error(test[target], predictions["predicted"], squared=False), \
               (predict_time * 1000) / test.shape[0]

    elif config_json["task"] == ":image_classification":
        return accuracy_score(y_test, predictions["predicted"]), (predict_time * 1000) / y_test.shape[0]

    elif config_json["task"] == ":image_regression":
        return mean_squared_error(y_test, predictions["predicted"], squared=False), \
               (predict_time * 1000) / y_test.shape[0]
    elif config_json["task"] == ":time_series_classification":
        train, test = dataloader(config_json)
        target = config_json["configuration"]["target"]["target"]

        test_target = test[target].astype("string")
        predicted_target = predictions["predicted"].astype("string")
        acc_score = accuracy_score(test_target, predicted_target)
        print("accuracy", acc_score)
        print("Classification Report \n",
              classification_report(test_target, predicted_target,zero_division=0)
              )
        return acc_score, (predict_time * 1000) / test.shape[0]


def predict(data, config_json, config_path):
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
                                        config_json["user_identifier"],
                                        config_json["training_id"],
                                        get_config_property("result-folder-name"))

    if config_json["task"] == ":time_series_classification":
        # Time Series Classification Task
        file_path = os.path.join(result_folder_location, "test.ts")
    else:
        file_path = os.path.join(result_folder_location, "test.csv")

    with open(file_path, "w+") as f:
        f.write(data)

    # predict
    os.chmod(os.path.join(result_folder_location, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(result_folder_location, "predict.py"), file_path, config_path])
    predict_time = time.time() - predict_start

    predictions = pd.read_csv(os.path.join(result_folder_location, "predictions.csv"))
    os.remove(file_path)
    os.remove(os.path.join(result_folder_location, "predictions.csv"))

    
    return 0, predict_time, predictions["predicted"].astype('string').tolist()

def SetupRunNewRunEnvironment(configuration):
    # saving AutoML configuration JSON
    config_json = json.loads(configuration)

    #folder location for job related files
    job_folder_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_identifier"],
                                        config_json["training_id"],
                                        get_config_property("job-folder-name"))

    #folder location for automl generated model files (not copied in ZIP)
    model_folder_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_identifier"],
                                        config_json["training_id"],
                                        get_config_property("model-folder-name"))

    export_folder_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_identifier"],
                                        config_json["training_id"],
                                        get_config_property("export-folder-name"))

    result_folder_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_identifier"],
                                        config_json["training_id"],
                                        get_config_property("result-folder-name"))

    config_json["job_folder_location"] = job_folder_location
    config_json["model_folder_location"] = model_folder_location
    config_json["export_folder_location"] = export_folder_location
    config_json["result_folder_location"] = result_folder_location

    #Make sure job folders exists
    os.makedirs(job_folder_location, exist_ok=True)
    os.makedirs(model_folder_location, exist_ok=True)
    os.makedirs(export_folder_location, exist_ok=True)
    os.makedirs(result_folder_location, exist_ok=True)

    #Save job file
    with open(os.path.join(job_folder_location, get_config_property("job-file-name")), "w+") as f:
        json.dump(config_json, f)
        
    return config_json

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

def read_tabular_dataset_training_data(json_configuration):
    """
    Read the training dataset from disk
    """
    delimiters = {
        "comma":        ",",
        "semicolon":    ";",
        "space":        " ",
        "tab":          "\t",
    }
    data = pd.read_csv(os.path.join(json_configuration["file_location"], json_configuration["file_name"]), delimiter=delimiters[json_configuration['file_configuration']['delimiter']], skiprows=(json_configuration['file_configuration']['start_row']-1), escapechar=json_configuration['file_configuration']['escape_character'], decimal=json_configuration['file_configuration']['decimal_character'])

    # convert all object columns to categories, because autosklearn only supports numerical,
    # bool and categorical features
    #TODO: change to ontology based preprocessing
    data[data.select_dtypes(['object']).columns] = data.select_dtypes(['object']).apply(lambda x: x.astype('category'))

    # split training set
    if SplitMethod.SPLIT_METHOD_RANDOM.value == json_configuration["test_configuration"]["method"]:
        train = data.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
        test = data.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
    else:
        train = data.iloc[:int(data.shape[0] * json_configuration["test_configuration"]["split_ratio"])]
        test = data.iloc[int(data.shape[0] * json_configuration["test_configuration"]["split_ratio"]):]

    return train, test

def prepare_tabular_dataset(df, json_configuration):
    """
    Prepare tabular dataset, perform feature preparation and data type casting
    """
    df = feature_preparation(df, json_configuration["dataset_configuration"]["features"].items())
    df = cast_dataframe_column(df, json_configuration["configuration"]["target"]["target"], json_configuration["configuration"]["target"]["type"])
    X = df.drop(json_configuration["configuration"]["target"]["target"], axis=1)
    y = df[json_configuration["configuration"]["target"]["target"]]
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

def read_image_dataset(json_configuration):
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
    data_dir = os.path.join(json_configuration["file_location"], json_configuration["file_name"])
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
