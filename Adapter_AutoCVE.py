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
from templates.TemplateGenerator import TemplateGenerator
from Utils.OsSpecific import in_cluster, on_unix


class AdapterServiceServicer(Adapter_pb2_grpc.AdapterServiceServicer):
    """ AutoML Adapter Service implementation. Service provide functionality to execute and interact with the current AutoML process. """

    def __init__(self):
        self = self

    def StartAutoML(self, request, context):
        """ 
        Execute a new AutoML run. 
        """
        try:
            # saving AutoML configuration JSON
            with open(get_config_property("job-file-name"), "w+") as f:
                json.dump(request.processJson, f)

            process = self.start_automl_process()
            yield from self.capture_process_output(process)
            self.generate_script()
            outputJson = self.zip_script()

            yield from self.get_response(outputJson)

        except Exception as e:
            return self.get_except_response(context, e)

    def get_except_response(self, context, e):
        print(e)
        context.set_details(f"Error while executing AutoCVE: {e}")
        context.set_code(grpc.StatusCode.UNAVAILABLE)
        return Adapter_pb2.StartAutoMLResponse()

    def generate_script(self):
        generator = TemplateGenerator()
        generator.generate_script()

    def capture_process_output(self, process):
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

    def get_response(self, outputJson):
        response = Adapter_pb2.StartAutoMLResponse()
        response.returnCode = Adapter_pb2.ADAPTER_RETURN_CODE_SUCCESS
        response.outputJson = json.dumps(outputJson)
        yield response

    def zip_script(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        export_zip_file_name = get_config_property("export-zip-file-name")
        if in_cluster():
            print("RUNNING DOCKER")
            if not os.path.exists("omaml/output"):  # ensure output folder exists
                os.makedirs("omaml/output")
            zip_content_path = os.path.join(BASE_DIR, "templates/output")
            shutil.make_archive(export_zip_file_name, 'zip', zip_content_path)
            shutil.move(f"{export_zip_file_name}.zip", "omaml/output/autocve-export.zip")
            outputJson = {"file_name": f"{export_zip_file_name}.zip"}
            outputJson.update({"file_location": "omaml/output/"})

        else:
            print("RUNNING LOCAL")
            zip_content_path = os.path.join(BASE_DIR, get_config_property("output-path"))
            shutil.make_archive(export_zip_file_name, 'zip', zip_content_path)
            outputJson = {"file_name": f"templates/output/{export_zip_file_name}.zip"}
            outputJson.update({"file_location": os.path.join(BASE_DIR, "MetaAutoML-Adapter-AutoCVE")})
        return outputJson

    def start_automl_process(self):
        """"
        starts the automl process with respect to the operating system
        @:return started automl process
        """
        return subprocess.Popen([get_config_property("python-environment"), "AutoML.py", ""],
                                stdout=subprocess.PIPE,
                                universal_newlines=True)


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
