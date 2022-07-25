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
from sklearn.metrics import accuracy_score, mean_squared_error

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

    return train_data, test_data


def export_model(model, trainingId, file_name):
    """
    Export the generated ML model to disk
    ---
    Parameter:
    1. generate ML model
    """
    with open(os.path.join(get_config_property('output-path'), trainingId, file_name), 'wb+') as file:
        dill.dump(model, file)

def start_automl_process():
    """"
    @:return started automl process
    """
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    return subprocess.Popen([python_env, "AutoML.py", ""],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)

def generate_script(config_json):
    """
    Generate the result python script
    ---
    Parameter
    1. process configuration
    """
    generator = TemplateGenerator()
    generator.generate_script(config_json)

def zip_script(training_id):
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
    output_path = get_config_property("output-path")
    training_path = os.path.join(output_path, str(training_id))
    tmp_base_folder = os.path.join(output_path, 'tmp')
    tmp_training_folder = os.path.join(tmp_base_folder, str(training_id))
    shutil.copy(get_config_property("predict-time-sources-path"),
                training_path)

    #create tmp if not already existing
    if not os.path.isdir(tmp_base_folder):
        os.mkdir(tmp_base_folder)

    shutil.make_archive(os.path.join(tmp_training_folder, zip_file_name),
                        'zip',
                        training_path,
                        base_dir=None)

    #copy zip from temp to training folder and delete tmp training zip
    shutil.copyfile(os.path.join(tmp_training_folder,  zip_file_name + '.zip'), os.path.join(training_path, zip_file_name + '.zip'))
    shutil.rmtree(tmp_training_folder)

    if get_config_property("local_execution") == "YES":
        file_loc_on_controller = os.path.join(output_path,
                                            str(training_id))
    else:
        file_loc_on_controller = os.path.join(output_path,
                                            get_config_property('adapter-name'),
                                            str(training_id))

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
    output_path = get_config_property("output-path")
    training_path = os.path.join(output_path, str(config_json["training_id"]))
    # predict
    os.chmod(os.path.join(training_path, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(training_path, "predict.py"), file_path, config_path])
    predict_time = time.time() - predict_start

    if(config_json["task"] == ":tabular_classification" or config_json["task"] == ":tabular_regression"):
        train, test = dataloader(config_json)
        target = config_json["configuration"]["target"]["target"]
    elif(config_json["task"] == ":image_classification" or config_json["task"] == ":image_regression"):
        X_train, y_train, X_val, y_val, X_test, y_test = data_loader(config_json)

    predictions = pd.read_csv(os.path.join(training_path, "predictions.csv"))

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
    working_dir = os.path.join(get_config_property("output-path"), "working_dir")

    shutil.unpack_archive(os.path.join(get_config_property("output-path"),
                                       str(config_json["training_id"]),
                                       get_config_property("export-zip-file-name") + ".zip"),
                          working_dir,
                          "zip")

    file_path = os.path.join(working_dir, "test.csv")

    with open(file_path, "w+") as f:
        f.write(data)

    # predict
    os.chmod(os.path.join(working_dir, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(working_dir, "predict.py"), file_path, config_path])
    predict_time = time.time() - predict_start

    test = pd.read_csv(file_path)

    predictions = pd.read_csv(os.path.join(working_dir, "predictions.csv"))
    shutil.rmtree(working_dir)

    
    return 0, predict_time, predictions["predicted"].astype('string').tolist()

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
    data = pd.read_csv(os.path.join(json_configuration["file_location"], json_configuration["file_name"]),
                    **json_configuration["file_configuration"])

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
    data_dir = os.path.join(json_configuration["file_location"], json_configuration["file_name"].replace(".zip", ""))
    train_df_list =[]
    vali_df_list =[]
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
    vali_df_list = read_image_dataset_folder("val")
    test_df_list = read_image_dataset_folder("test")

    train_data = pd.concat(train_df_list, axis=0,ignore_index=True)
    vali_data = pd.concat(vali_df_list, axis=0,ignore_index=True)
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
    X_val = np.array([img_preprocess(p) for p in vali_data.name.values])
    y_val = vali_data.outcome.values
    X_test = np.array([img_preprocess(p) for p in test_data.name.values])
    y_test = test_data.outcome.values
    return X_train, y_train, X_val, y_val, X_test, y_test
    
#endregion