from predict_time_sources import feature_preparation, DataType, SplitMethod
from JsonUtil import get_config_property
import numpy as np
import pandas as pd
import os
import grpc
import subprocess
import time
import sys
import json
import shutil
import Adapter_pb2
import Adapter_pb2_grpc
from TemplateGenerator import TemplateGenerator
from sklearn.metrics import mean_squared_error, accuracy_score

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
    temp_path = os.path.join(output_path, 'tmp')

    # remove files from earlier runs
    if os.path.exists(os.path.join(session_path, zip_file_name + '.zip')):
        os.remove(os.path.join(session_path, zip_file_name + '.zip'))

    # copy all files required for prediction into temp folder, so they will also be zipped
    shutil.copy(get_config_property("predict-time-sources-path"),
                temp_path)

    shutil.make_archive(os.path.join(session_path, zip_file_name),
                        'zip',
                        temp_path)
    for f in os.listdir(output_path):
        if f not in ('.gitkeep', 'tmp', *(str(i) for i in range(1, session_id + 1))):
            file_path = os.path.join(output_path, f)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)

    file_loc_on_controller = os.path.join(output_path,
                                          get_config_property('adapter-name'),
                                          str(session_id))

    return {
        'file_name': f'{zip_file_name}.zip',
        'file_location': file_loc_on_controller
    }

def evaluate(config_json, config_path):
    """
    Evaluate the model by using the test set
    ---
    Parameter
    1. configuration json
    1. configuration path
    ---
    Return evaluation score
    """
    file_path = os.path.join(config_json["file_location"], config_json["file_name"])
    working_dir = os.path.join(get_config_property("output-path"), "working_dir")
    #Setup working directory
    shutil.unpack_archive(os.path.join(get_config_property("output-path"),
                                       str(config_json["session_id"]),
                                       get_config_property("export-zip-file-name") + ".zip"),
                          working_dir,
                          "zip")
    # predict
    os.chmod(os.path.join(working_dir, "predict.py"), 0o777)
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    predict_start = time.time()
    subprocess.call([python_env, os.path.join(working_dir, "predict.py"), file_path, config_path])
    predict_time = time.time() - predict_start

    test = pd.read_csv(file_path)
    if SplitMethod.SPLIT_METHOD_RANDOM == config_json["test_configuration"]["method"]:
        test = test.sample(random_state=config_json["test_configuration"]["random_state"], frac=1)
    else:
        test = test.iloc[int(test.shape[0] * config_json["test_configuration"]["split_ratio"]):]

    predictions = pd.read_csv(os.path.join(working_dir, "predictions.csv"))
    #Cleanup working directory
    shutil.rmtree(working_dir)

    target = config_json["tabular_configuration"]["target"]["target"]
    if config_json["task"] == 1:
        return accuracy_score(test[target], predictions["predicted"]), (predict_time * 1000) / test.shape[
            0]
    elif config_json["task"] == 2:
        return mean_squared_error(test[target], predictions["predicted"], squared=False), \
               (predict_time * 1000) / test.shape[0]


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

    target = config_json["tabular_configuration"]["target"]["target"]
    if config_json["task"] == 1 and target in test:
        return accuracy_score(test[target], predictions["predicted"]), predict_time, \
               predictions["predicted"].astype('string').tolist()
    elif config_json["task"] == 2 and target in test:
        return mean_squared_error(test[target], predictions["predicted"], squared=False), predict_time, \
               predictions["predicted"].astype(np.string).tolist()
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
    df = pd.read_csv(os.path.join(json_configuration["file_location"], json_configuration["file_name"]),
                    **json_configuration["file_configuration"])

    # split training set
    if SplitMethod.SPLIT_METHOD_RANDOM == json_configuration["test_configuration"]["method"]:
        df = df.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
    else:
        df = df.iloc[:int(df.shape[0] * json_configuration["test_configuration"]["split_ratio"])]

    return df

def prepare_tabular_dataset(df, json_configuration):
    """
    Prepare tabular dataset, perform feature preparation and data type casting
    """
    df = feature_preparation(df, json_configuration["tabular_configuration"]["features"].items())
    df = cast_dataframe_column(df, json_configuration["tabular_configuration"]["target"]["target"], json_configuration["tabular_configuration"]["target"]["type"])
    X = df.drop(json_configuration["tabular_configuration"]["target"]["target"], axis=1)
    y = df[json_configuration["tabular_configuration"]["target"]["target"]]
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