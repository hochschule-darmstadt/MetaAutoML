import grpc
import os
import logging
import json
import time
import shutil

from autogluon.tabular import TabularPredictor

import Adapter_pb2
import Adapter_pb2_grpc

from concurrent import futures
from JsonUtil import get_config_property

from AdapterUtils import *

def GetMetaInformations(config_json):
    working_dir = os.path.join(get_config_property("output-path"), "working_dir")
    shutil.unpack_archive(os.path.join(get_config_property("output-path"),
        str(config_json["session_id"]),
        get_config_property("export-zip-file-name") + ".zip"),
        working_dir,
        "zip")
    # extract additional information from automl
    automl = TabularPredictor.load(os.path.join(os.path.join(get_config_property("output-path"), "working_dir"), 'model_gluon.gluon'))
    automl_info = automl._learner.get_info(include_model_info=True)
    librarylist = set()
    model = automl_info['best_model']
    for model_info in automl_info['model_info']:
        if model_info == model:
            pass
        elif model_info in ('LightGBM', 'LightGBMXT'):
            librarylist.add("lightgbm")
        elif model_info == 'XGBoost':
            librarylist.add("xgboost")
        elif model_info == 'CatBoost':
            librarylist.add("catboost")
        elif model_info == 'NeuralNetFastAI':
            librarylist.add("pytorch")
        else:
            librarylist.add("sklearn")
    library = " + ".join(librarylist)
    shutil.rmtree(working_dir)
    return library, model

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


            library, model = GetMetaInformations(config_json)
            test_score, prediction_time= evaluate(config_json, job_file_location)
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
