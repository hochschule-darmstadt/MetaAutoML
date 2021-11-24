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
from OsSpecific import in_cluster


def get_except_response(context, e):
    print(e)
    adapter_name = get_config_property("adapter-name")
    context.set_details(f"Error while executing {adapter_name}: {e}")
    context.set_code(grpc.StatusCode.UNAVAILABLE)
    return Adapter_pb2.StartAutoMLResponse()


def generate_script(config_json):
    generator = TemplateGenerator()
    generator.generate_script(config_json)


def capture_process_output(process):
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
            yield process_update
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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_zip_file_name = get_config_property("export-zip-file-name")
    templates_output_path = get_config_property("templates-output-path")
    if in_cluster():
        print("RUNNING DOCKER")
        output_path = get_config_property("output-path-docker")
        if not os.path.exists(output_path):  # ensure output folder exists
            os.makedirs(output_path)

        zip_contents_path = os.path.join(base_dir, templates_output_path)
        shutil.make_archive(export_zip_file_name, 'zip', zip_contents_path)
        shutil.move(f"{export_zip_file_name}.zip", f"{output_path}/{export_zip_file_name}.zip")
        output_json = {"file_name": f"{export_zip_file_name}.zip"}
        output_json.update({"file_location": f"{output_path}/"})

    else:
        print("RUNNING LOCAL")
        repository_dir_name = get_config_property("repository-dir-name")
        zip_contents_path = os.path.join(base_dir, repository_dir_name, templates_output_path)
        shutil.make_archive(export_zip_file_name, 'zip', zip_contents_path)
        output_json = {"file_name": f"{export_zip_file_name}.zip"}
        output_json.update({"file_location": os.path.join(base_dir, repository_dir_name)})

    return output_json


def start_automl_process():
    """"
    @:return started automl process
    """
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    return subprocess.Popen([python_env, "AutoML.py", ""],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)


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
            # saving AutoML configuration JSON
            config_json = json.loads(request.processJson)
            with open(get_config_property("job-file-name"), "w+") as f:
                json.dump(config_json, f)

            process = start_automl_process()
            yield from capture_process_output(process)
            generate_script(config_json)
            output_json = zip_script()

            yield from get_response(output_json)

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
    print(get_config_property("adapter-name") + " started")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
    print('done.')
