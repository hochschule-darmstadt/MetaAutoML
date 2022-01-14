import grpc
import os
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
from Utils.JsonUtil import get_config_property
from StructuredDataAutoML import SplitMethod


def get_except_response(context, e):
    print(e)
    adapter_name = get_config_property("adapter-name")
    context.set_details(f"Error while executing {adapter_name}: {e}")
    context.set_code(grpc.StatusCode.UNAVAILABLE)
    return Adapter_pb2.StartAutoMLResponse()


def generate_script(config_json):
    generator = TemplateGenerator()
    generator.generate_script(config_json)


def capture_process_output(process, start_time):
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
            yield process_update
            sys.stdout.write(capture)
            sys.stdout.flush()
            capture = ""
        capture += s
        s = process.stdout.read(1)


def get_response(output_json, start_time, test_score):
    response = Adapter_pb2.StartAutoMLResponse()
    response.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS
    response.outputJson = json.dumps(output_json)
    response.runtime = int(time.time() - start_time)
    response.testScore = test_score
    response.validationScore = 0.0
    yield response


def zip_script(session_id):
    zip_file_name = get_config_property("export-zip-file-name")
    output_path = get_config_property("output-path")
    session_path = os.path.join(output_path, str(session_id))

    print(f"saving model zip file for {get_config_property('adapter-name')}")

    if os.path.exists(os.path.join(session_path, zip_file_name + '.zip')):
        os.remove(os.path.join(session_path, zip_file_name + '.zip'))

    shutil.make_archive(os.path.join(session_path, zip_file_name),
                        'zip',
                        os.path.join(output_path, 'tmp'))
    for f in os.listdir(output_path):
        if f not in ('.gitkeep', 'tmp', *(str(i) for i in range(1, session_id + 1))):
            file_path = os.path.join(output_path, f)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
    return {"file_name": f'{zip_file_name}.zip', "file_location": session_path}


def start_automl_process():
    """"
    @:return started automl process
    """
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    return subprocess.Popen([python_env, "AutoML.py", ""],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)


def evaluate(config_json, config_path):
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
    subprocess.call([python_env, os.path.join(working_dir, "predict.py"), file_path, config_path])

    test = pd.read_csv(file_path)
    if SplitMethod.SPLIT_METHOD_RANDOM == config_json["test_configuration"]["method"]:
        test = test.sample(random_state=config_json["test_configuration"]["random_state"], frac=1)
    test = test.iloc[int(test.shape[0] * config_json["test_configuration"]["split_ratio"]):]

    predictions = pd.read_csv(os.path.join(working_dir, "predictions.csv"))
    shutil.rmtree(working_dir)

    target = config_json["tabular_configuration"]["target"]["target"]
    if config_json["task"] == 1:
        return accuracy_score(test[target], predictions["predicted"])
    elif config_json["task"] == 2:
        return mean_squared_error(test[target], predictions["predicted"], squared=False)


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

            test_score = evaluate(config_json, job_file_location)

            response = yield from get_response(output_json, start_time, test_score)
            print(f'{get_config_property("adapter-name")} job finished')
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
