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
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sktime.datatypes import convert_to
from sktime.datasets import load_from_tsfile_to_dataframe

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


def capture_process_output(process, start_time):
    """
    Read console log from subprocess, and send it after each \n to the controller
    ---
    Parameter
    1. system process representing the AutoML process
    2. Process start time
    """
    capture = ""
    s = process.stdout.read(1)
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
        capture += s
        s = process.stdout.read(1)


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
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == ":tabular_regression":
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == ":image_classification":
        return read_image_dataset(config)
    elif config["task"] == ":image_regression":
        return read_image_dataset(config)
    elif config["task"] == ":time_series_classification":
        return read_longitudinal_dataset(config)

    return train_data, test_data


def export_model(model, sessionId, file_name):
    """
    Export the generated ML model to disk
    ---
    Parameter:
    1. generate ML model
    """
    with open(os.path.join(get_config_property('output-path'), sessionId, file_name), 'wb+') as file:
        dill.dump(model, file)


def export_keras_model(model, sessionId, file_name):
    """
    Saves the given keras model
    ---
    Parameter:
    1. keras model
    2. session id
    3. file name
    """
    save_path = os.path.join(get_config_property('output-path'), sessionId, file_name)
    model.save(save_path)


def export_label_binarizer(label_binarizer, sessionId, file_name):
    """
    Saves the given instance of the sklearn.preprocessing.LabelBinarizer class
    ---
    Parameter:
    1. instance of LabelBinarizer
    2. session id
    3. file name
    """
    with open(os.path.join(get_config_property('output-path'), sessionId, file_name), 'wb+') as file:
        dill.dump(label_binarizer, file)


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

def zip_script(session_id):
    """
    Zip the model and script from the current run
    ---
    Parameter
    1. current run session id
    ---
    Return json with zip information
    """
    print(f"saving model zip file for {get_config_property('adapter-name')}")

    zip_file_name = get_config_property("export-zip-file-name")
    output_path = get_config_property("output-path")
    session_path = os.path.join(output_path, str(session_id))
    tmp_base_folder = os.path.join(output_path, 'tmp')
    tmp_session_folder = os.path.join(tmp_base_folder, str(session_id))
    shutil.copy(get_config_property("predict-time-sources-path"),
                session_path)

    #create tmp if not already existing
    if not os.path.isdir(tmp_base_folder):
        os.mkdir(tmp_base_folder)

    shutil.make_archive(os.path.join(tmp_session_folder, zip_file_name),
                        'zip',
                        session_path,
                        base_dir=None)

    #copy zip from temp to session folder and delete tmp session zip
    shutil.copyfile(os.path.join(tmp_session_folder,  zip_file_name + '.zip'), os.path.join(session_path, zip_file_name + '.zip'))
    shutil.rmtree(tmp_session_folder)

    if get_config_property("local_execution") == "YES":
        file_loc_on_controller = os.path.join(output_path,
                                            str(session_id))
    else:
        file_loc_on_controller = os.path.join(output_path,
                                            get_config_property('adapter-name'),
                                            str(session_id))

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
    session_path = os.path.join(output_path, str(config_json["session_id"]))
    # predict
    os.chmod(os.path.join(session_path, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(session_path, "predict.py"), file_path, config_path])
    predict_time = time.time() - predict_start

    train, test = dataloader(config_json)
    predictions = pd.read_csv(os.path.join(session_path, "predictions.csv"))
    target = config_json["configuration"]["target"]["target"]

    if config_json["task"] == ":tabular_classification":
        return accuracy_score(test[target], predictions["predicted"]), (predict_time * 1000) / test.shape[0]

    elif config_json["task"] == ":tabular_regression":
        return mean_squared_error(test[target], predictions["predicted"], squared=False), \
               (predict_time * 1000) / test.shape[0]

    elif config_json["task"] == ":image_classification":
        return accuracy_score(predictions["label"], predictions["predicted"]), (predict_time * 1000) / predictions.shape[0]

    elif config_json["task"] == ":image_regression":
        return mean_squared_error(test.y, predictions["predicted"], squared=False), \
               (predict_time * 1000) / predictions.shape[0]
    elif config_json["task"] == ":time_series_classification":
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
    working_dir = os.path.join(get_config_property("output-path"), "working_dir")

    shutil.unpack_archive(os.path.join(get_config_property("output-path"),
                                       str(config_json["session_id"]),
                                       get_config_property("export-zip-file-name") + ".zip"),
                          working_dir,
                          "zip")

    # file_path = os.path.join(working_dir, "test.csv")
    if config_json["task"] == ":time_series_classification":
        # Time Series Classification Task
        file_path = os.path.join(working_dir, "test.ts")
    else:
        file_path = os.path.join(working_dir, "test.csv")

    with open(file_path, "w+") as f:
        f.write(data)

    # predict
    os.chmod(os.path.join(working_dir, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(working_dir, "predict.py"), file_path, config_path])
    predict_time = time.time() - predict_start

    # test = pd.read_csv(file_path)
    if config_json["task"] == ":time_series_classification":
        # Time Series Classification Task
        test = load_from_tsfile_to_dataframe(file_path, return_separate_X_and_y=False)
        test = test.rename(columns={"class_vals": "target"})
    else:
        test = pd.read_csv(file_path)

    predictions = pd.read_csv(os.path.join(working_dir, "predictions.csv"))
    shutil.rmtree(working_dir)

    target = config_json["tabular_configuration"]["target"]["target"]
    if config_json["task"] == 1 and target in test:
        return accuracy_score(test[target], predictions["predicted"]), predict_time, \
               predictions["predicted"].astype('string').tolist()
    elif config_json["task"] == 2 and target in test:
        return mean_squared_error(test[target], predictions["predicted"], squared=False), predict_time, \
               predictions["predicted"].astype(np.string).tolist()
    elif config_json["task"] == ":time_series_classification" and target in test:
        acc_score = accuracy_score(test[target].astype("string"), predictions["predicted"].astype("string"))
        return acc_score, predict_time, predictions["predicted"].astype('string').tolist()
    else:
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

    local_dir_path = json_configuration["file_location"]

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
    session_dir = os.path.join(get_config_property("output-path"), json_configuration["session_id"])
    data_dir = os.path.join(local_dir_path, json_configuration["file_name"])
    shutil.unpack_archive(data_dir, session_dir)
    files_train = []
    dataset_folder_name = json_configuration["file_name"].replace(".zip", "")
    for folder in os.listdir(os.path.join(session_dir, dataset_folder_name, "train")):
        files_train.append(glob.glob(os.path.join(session_dir, dataset_folder_name, "train", folder, "*.jpeg")))

    train_df_list =[]
    for i in range(len(files_train)):
        df = pd.DataFrame()
        df["name"] = [x for x in files_train[i]]
        df['outcome'] = i
        train_df_list.append(df)
    
    train_data = pd.concat(train_df_list, axis=0,ignore_index=True)
    files_valid = []
    dataset_folder_name = json_configuration["file_name"].replace(".zip", "")
    for folder in os.listdir(os.path.join(session_dir, dataset_folder_name, "train")):
        files_valid.append(glob.glob(os.path.join(session_dir, dataset_folder_name, "val", folder, "*.jpeg")))

    vali_df_list =[]
    for i in range(len(files_valid)):
        df = pd.DataFrame()
        df["name"] = [x for x in files_valid[i]]
        df['outcome'] = i
        vali_df_list.append(df)
    
    vali_data = pd.concat(vali_df_list, axis=0,ignore_index=True)

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
    return X_train, y_train, X_val, y_val
    """
    if(json_configuration["test_configuration"]["dataset_structure"] == 1):
        train_data = ak.image_dataset_from_directory(
            data_dir,
            validation_split=json_configuration["test_configuration"]["split_ratio"],
            subset="training",
            seed=123,
            image_size=(json_configuration["test_configuration"]["image_height"], 
                        json_configuration["test_configuration"]["image_width"]),
            batch_size=json_configuration["test_configuration"]["batch_size"],
        )

        test_data = ak.image_dataset_from_directory(
            data_dir,
            validation_split=json_configuration["test_configuration"]["split_ratio"],
            subset="validation",
            seed=123,
            image_size=(json_configuration["test_configuration"]["image_height"], 
                        json_configuration["test_configuration"]["image_width"]),
            batch_size=json_configuration["test_configuration"]["batch_size"],
        )

    else:
        train_data = ak.image_dataset_from_directory(
            os.path.join(data_dir, "train"),
            image_size=(json_configuration["test_configuration"]["image_height"], 
                        json_configuration["test_configuration"]["image_width"]),
            batch_size = json_configuration["test_configuration"]["batch_size"]
        )

        test_data = ak.image_dataset_from_directory(
            os.path.join(data_dir, "test"), 
            shuffle=False,
            image_size=(json_configuration["test_configuration"]["image_height"], 
                        json_configuration["test_configuration"]["image_width"]),
            batch_size=json_configuration["test_configuration"]["batch_size"]
        )
    return train_data, vali_data
    """

#endregion

######################################################################
## LONGITUDINAL DATASET HELPER FUNCTIONS
######################################################################

#region


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


def read_longitudinal_dataset(json_configuration):
    """
    Read longitudinal data from the `.ts` file
    """
    file_path = os.path.join(json_configuration["file_location"], json_configuration["file_name"])
    dataset = load_from_tsfile_to_dataframe(file_path, return_separate_X_and_y=False)
    dataset = dataset.rename(columns={"class_vals": "target"})
    return split_dataset(dataset, json_configuration)


def convert_longitudinal_to_numpy(X, y, label_binarizer):
    """
    Convert the panel dataset to numpy3D
    """
    X_np = convert_to(X, to_type="numpy3D")
    y_binary = label_binarizer.transform(y)
    return X_np, y_binary

#endregion