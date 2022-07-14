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
import pandas as pd
from AdapterUtils import *
from JsonUtil import get_config_property


def GetMetaInformation(config_json):
    working_dir = os.path.join(get_config_property("output-path"), config_json["session_id"])
    leaderboard = pd.read_csv(os.path.join(working_dir, "Models", "leaderboard.csv"))
    #print(leaderboard[leaderboard["metric_value"].eq(leaderboard["metric_value"].min())])
    model = leaderboard[leaderboard["metric_value"].eq(leaderboard["metric_value"].min())]["model_type"].values[0]
    library = leaderboard[leaderboard["metric_value"].eq(leaderboard["metric_value"].min())]["model_type"].values[0]
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
            yield from capture_process_output(process, start_time, False)
            generate_script(config_json)
            output_json = zip_script(config_json["session_id"])
            library, model = GetMetaInformation(config_json)
            test_score, prediction_time = evaluate(config_json, job_file_location, data_loader)
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
    if not os.path.exists('app-data/output/tmp'):
        os.mkdir('app-data/output/tmp')
    logging.basicConfig()
    serve()
    print('done.')
