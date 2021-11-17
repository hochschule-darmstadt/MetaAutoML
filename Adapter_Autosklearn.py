import grpc
import os
import sys
import logging
import shutil
import subprocess
import json
from Utils.JsonUtil import get_config_property

import Adapter_pb2
import Adapter_pb2_grpc

from concurrent import futures
from TemplateGenerator import TemplateGenerator
from OsSpecific import in_cluster, on_unix


def get_except_response(context, e):
    print(e)
    context.set_details(f"Error while executing AutoKeras: {e}")
    context.set_code(grpc.StatusCode.UNAVAILABLE)
    return Adapter_pb2.StartAutoMLResponse()


def generate_script():
    generator = TemplateGenerator()
    generator.GenerateScript()


def capture_process_output(process):
    capture = ""
    s = process.stdout.read(1)
    capture += s
    # Run until no more output is produced by the subprocess
    while len(s) > 0:
        if capture[len(capture) - 1] == '\n':
            processUpdate = Adapter_pb2.StartAutoMLResponse()
            processUpdate.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_STATUS_UPDATE
            processUpdate.statusUpdate = capture
            processUpdate.outputJson = ""
            yield processUpdate
            sys.stdout.write(capture)
            sys.stdout.flush()
            capture = ""
        capture += s
        s = process.stdout.read(1)


def get_response(output_json):
    response = Adapter_pb2.StartAutoMLResponse()
    response.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS
    response.outputJson = json.dumps(output_json)
    yield response


def zip_script():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXPORT_ZIP_FILE_NAME = get_config_property("export-zip-file-name")
    TEMPLATES_OUTPUT_PATH = get_config_property("templates-output-path")
    if in_cluster():
        print("RUNNING DOCKER")
        OUTPUT_PATH = get_config_property("output-path-docker")
        if not os.path.exists(OUTPUT_PATH):  # ensure output folder exists
            os.makedirs(OUTPUT_PATH)

        ZIP_CONTENTS_PATH = os.path.join(BASE_DIR, TEMPLATES_OUTPUT_PATH)
        shutil.make_archive(EXPORT_ZIP_FILE_NAME, 'zip', ZIP_CONTENTS_PATH)
        shutil.move(f"{EXPORT_ZIP_FILE_NAME}.zip", f"{OUTPUT_PATH}/{EXPORT_ZIP_FILE_NAME}.zip")
        output_json = {"file_name": f"{EXPORT_ZIP_FILE_NAME}.zip"}
        output_json.update({"file_location": f"{OUTPUT_PATH}/"})

    else:
        print("RUNNING LOCAL")
        REPOSITORY_DIR_NAME = get_config_property("repository-dir-name")
        ZIP_CONTENTS_PATH = os.path.join(BASE_DIR, REPOSITORY_DIR_NAME, TEMPLATES_OUTPUT_PATH)
        shutil.make_archive(EXPORT_ZIP_FILE_NAME, 'zip', ZIP_CONTENTS_PATH)
        output_json = {"file_name": f"{EXPORT_ZIP_FILE_NAME}.zip"}
        output_json.update({"file_location": os.path.join(BASE_DIR, REPOSITORY_DIR_NAME)})

    return output_json


def start_automl_process():
    """"
    starts the automl process with respect to the operating system
    @:return started automl process
    """
    python_env = None
    if in_cluster():
        python_env = get_config_property("python-env-docker")
    else:
        # Requires env var to be set to desired python environment on local execution
        python_env = os.getenv("PYTHON_ENV", default=None)

    return subprocess.Popen([python_env, "AutoML.py", ""],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)


class AdapterServiceServicer(Adapter_pb2_grpc.AdapterServiceServicer):
    """ AutoML Adapter Service implementation. Service provide functionality to execute and interact with the current AutoML process. """

    def __init__(self):
        pass

    def StartAutoML(self, request, context):
        """ 
        Execute a new AutoML run. 
        """
        try:
            # saving AutoML configuration JSON
            with open(get_config_property("job-file-name"), "w+") as f:
                json.dump(request.processJson, f)

            process = start_automl_process()
            yield from capture_process_output(process)
            generate_script()
            outputJson = zip_script()

            yield from get_response(outputJson)

        except Exception as e:
            return get_except_response(context, e)


def serve():
    """
    Boot the gRPC server and wait for incoming connections
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Adapter_pb2_grpc.add_AdapterServiceServicer_to_server(AdapterServiceServicer(), server)
    server.add_insecure_port(get_config_property("grpc-server-address"))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
    print('done.')
