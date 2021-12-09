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
    # AutoGluon writes to stderr which seems to be not configurable
    s = process.stderr.read(1)
    capture += s
    # Run until no more output is produced by the subprocess
    while len(s) > 0:
        if capture[len(capture) - 1] == '\n':
            processUpdate = Adapter_pb2.StartAutoMLResponse()
            processUpdate.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_STATUS_UPDATE
            processUpdate.statusUpdate = capture
            processUpdate.outputJson = ""
            yield processUpdate
            sys.stderr.write(capture)
            sys.stderr.flush()
            capture = ""
        capture += s
        s = process.stderr.read(1)


def get_response(output_json):
    response = Adapter_pb2.StartAutoMLResponse()
    response.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS
    response.outputJson = json.dumps(output_json)
    yield response


def zip_script():
    zip_file_name = get_config_property("export-zip-file-name")
    output_path = get_config_property("output-path")

    print(f"saving model zip file for {get_config_property('adapter-name')}")

    shutil.make_archive(zip_file_name,
                        'zip',
                        output_path)
    shutil.move(f'{zip_file_name}.zip', output_path)

    return {"file_name": f'{zip_file_name}.zip',
            "file_location": output_path}


def start_automl_process():
    """"
    @:return started automl process
    """
    python_env = os.getenv("PYTHON_ENV", default="PYTHON_ENV_UNSET")

    return subprocess.Popen([python_env, "AutoML.py", ""],
                            stderr=subprocess.PIPE,
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
            job_file_location = os.path.join(get_config_property("job-file-path"),
                                             get_config_property("job-file-name"))
            with open(job_file_location, "w+") as f:
                json.dump(config_json, f)

            process = start_automl_process()
            yield from capture_process_output(process)
            generate_script(config_json)
            output_json = zip_script()

            response = yield from get_response(output_json)
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
