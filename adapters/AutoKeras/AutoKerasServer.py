import os

import numpy as np
import sys
import logging
import shutil
import subprocess
import json
import time
from concurrent import futures

import grpc
import pandas as pd
from sklearn.metrics import mean_squared_error, accuracy_score

import Adapter_pb2
import Adapter_pb2_grpc

from TemplateGenerator import TemplateGenerator
from JsonUtil import get_config_property
from predict_time_sources import SplitMethod

from AdapterUtils import *







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

    model = "neural network"
    library = "keras"

    test = pd.read_csv(file_path)
    if SplitMethod.SPLIT_METHOD_RANDOM == config_json["test_configuration"]["method"]:
        test = test.sample(random_state=config_json["test_configuration"]["random_state"], frac=1)
    else:
        test = test.iloc[int(test.shape[0] * config_json["test_configuration"]["split_ratio"]):]

    predictions = pd.read_csv(os.path.join(working_dir, "predictions.csv"))
    shutil.rmtree(working_dir)

    target = config_json["tabular_configuration"]["target"]["target"]
    if config_json["task"] == 1:
        return accuracy_score(test[target], predictions["predicted"]), (predict_time * 1000) / test.shape[
            0], library, model
    elif config_json["task"] == 2:
        return mean_squared_error(test[target], predictions["predicted"], squared=False), \
               (predict_time * 1000) / test.shape[0], library, model


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


class AdapterServiceServicer(Adapter_pb2_grpc.AdapterServiceServicer):
    """
    AutoML Adapter Service implementation.
    Service provide functionality to execute and interact with the current AutoML process.
    """

    def StartAutoML(self, request, context):
        """
        Execute a new AutoML run.
        """
        try:
            start_time = time.time()
            # saving AutoML configuration JSON
            config_json = json.loads(request.processJson)
            job_file_location = os.path.join(get_config_property("job-file-path"),
                                             get_config_property("job-file-name"))
            with open(job_file_location, "w+") as f:
                json.dump(config_json, f)

            process = start_automl_process()
            yield from capture_process_output(process, start_time)
            generate_script(config_json)
            output_json = zip_script(config_json["session_id"])

            test_score, prediction_time, library, model = evaluate(config_json, job_file_location)
            response = yield from get_response(output_json, start_time, test_score, prediction_time, library, model)
            print(f'{get_config_property("adapter-name")} job finished')
            return response

        except Exception as e:
            return get_except_response(context, e)

    def TestAdapter(self, request, context):
        try:
            # saving AutoML configuration JSON
            config_json = json.loads(request.processJson)
            job_file_location = os.path.join(get_config_property("job-file-path"),
                                             get_config_property("job-file-name"))
            with open(job_file_location, "w+") as f:
                json.dump(config_json, f)

            test_score, prediction_time, predictions = predict(request.testData, config_json, job_file_location)
            response = Adapter_pb2.TestAdapterResponse(predictions=predictions)
            response.score = test_score
            response.predictiontime = prediction_time
            return response

        except Exception as e:
            return get_except_response(context, e)


def serve():
    """
    Boot the gRPC server and wait for incoming connections
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Adapter_pb2_grpc.add_AdapterServiceServicer_to_server(AdapterServiceServicer(), server)
    server.add_insecure_port(f'{get_config_property("grpc-server-address")}:{os.getenv("GRPC_SERVER_PORT")}')
    server.start()
    print(get_config_property("adapter-name") + " started")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
    print('done.')
