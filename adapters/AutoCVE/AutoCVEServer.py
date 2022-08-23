import json
import logging
import os
import pickle
import shutil
import time
from concurrent import futures

import Adapter_pb2
import Adapter_pb2_grpc
import grpc
from AdapterUtils import *
from JsonUtil import get_config_property


def GetMetaInformation(config_json):
    """
    Get AutoCVE result Meta Information
    ---
    Parameter
    1. configuration json
    ---
    Return ML library name and model type
    """
    # extract additional information from automl
    with open(os.path.join(config_json["result_folder_location"], 'autocve-model.p'), 'rb') as file:
        automl = pickle.load(file)
        # check if xgb library is used as atleast one of the estimators
        library = ":scikit_learn_lib"
        if "xgbclassifier" in str(automl.estimators):
            #library = ":scikit_learn_lib + :xgboost_lib"
            library = ":xgboost_lib"
        model = ":ensemble"
    return library, model

class AdapterServiceServicer(Adapter_pb2_grpc.AdapterServiceServicer):
    """
    AutoML Adapter Service implementation.
    Service provide functionality to execute and interact with the current AutoML process.
    """
    def __init__(self):
        """
        These variables are used by the ExplainModel function.
        """
        self._automl = None
        self._loaded_training_id = None

    def StartAutoML(self, request, context):
        """
        Execute a new AutoML run.
        """
        try:
            start_time = time.time()
            # saving AutoML configuration JSON
            config = SetupRunNewRunEnvironment(request.processJson)

            process = start_automl_process(config)
            yield from capture_process_output(process, start_time, False)
            generate_script(config)
            output_json = zip_script(config)
            library, model = GetMetaInformation(config)
            test_score, prediction_time  = evaluate(config, os.path.join(config["job_folder_location"], get_config_property("job-file-name")), data_loader)

            response = yield from get_response(output_json, start_time, test_score, prediction_time, library, model)
            print(f'{get_config_property("adapter-name")} job finished')
            return response

        except Exception as e:
            return get_except_response(context, e)

    def TestAdapter(self, request, context):
        try:
            # saving AutoML configuration JSON
            config_json = json.loads(request.processJson)
            job_file_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_identifier"],
                                        config_json["training_id"],
                                        get_config_property("job-folder-name"),
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
