import json
import logging
import os
import shutil

from autogluon.tabular import TabularPredictor
from autogluon.vision import ImagePredictor, ImageDataset

import Adapter_pb2
import Adapter_pb2_grpc
import grpc
from AdapterUtils import *
from autogluon.tabular import TabularPredictor
from JsonUtil import get_config_property


from AdapterUtils import *


def data_loader(config):
    """
    Get exception message
    ---
    Parameter
    1. config: Job config
    ---
    Return job type specific dataset
    """
    train_data = None
    test_data = None

    if config["task"] == 1:
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == 2:
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == 3:
        train_data, test_data = None
    elif config["task"] == 4:
        train_data, test_data = read_image_dataset(config)
    elif config["task"] == 5:
        train_data, test_data = read_image_dataset(config)

    return train_data, test_data



def AutoGluon_data_loader():

    """
    Get exception message
    ---
    Parameter
    1. config: Job config
    ---
    Return job type specific dataset
    """
    train_data = None
    test_data = None

    if config["task"] == 1:
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == 2:
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == 3:
        train_data, test_data = None
    elif config["task"] == 4:
        train_data, test_data = read_image_dataset_auto_gluon(config)
    
    return train_data, test_data

def read_image_dataset_auto_gluon():

    """Reads image data and return sets
    ---
    Parameter
    1. config: Job config
    ---
    Return image dataset
    """

    local_dir_path = json_configuration["file_location"]

    data_dir = os.path.join(local_dir_path, json_configuration["file_name"])
    train_data = None
    test_data = None

    if(json_configuration["test_configuration"]["dataset_structure"] == 1):

        all_data = ImageDataset.from_folder(data_dir)
        train_data, val_data, test_data = all_data.random_split(val_size=json_configuration["test_configuration"]["split_ratio"], test_size=json_configuration["test_configuration"]["split_ratio"])


    else:
        train_data, val_data, test_data = ImageDataset.from_folders(data_dir)

    return train_data, test_data


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
            yield from capture_process_output(process, start_time, True)
            generate_script(config_json)
            output_json = zip_script(config_json["session_id"])


            library, model = GetMetaInformations(config_json)
            test_score, prediction_time= evaluate(config_json, job_file_location,AutoGluon_data_loader)
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

    # ToDo:
    # - Make image tasks available in frontend 
    # - Test image task application wide
    # 
    # Local testing
    # channel = grpc.insecure_channel(f'{get_config_property("grpc-server-address")}:{os.getenv("GRPC_SERVER_PORT")}')
    # stub = Adapter_pb2_grpc.AdapterServiceStub(channel)
    # request = Adapter_pb2.StartAutoMLRequest() 
    # 
    # job_file_location = os.path.join(get_config_property("job-file-path"),
    #                                 get_config_property("job-file-name"))
    # with open(job_file_location) as file:
    #     request.processJson = json.dumps(json.load(file))
    # 
    # response = stub.StartAutoML(request)

    print(get_config_property("adapter-name") + " started")
    server.wait_for_termination()


if __name__ == '__main__':
    if not os.path.exists('app-data/output/tmp'):
        os.mkdir('app-data/output/tmp')
    logging.basicConfig()
    serve()
    print('done.')
