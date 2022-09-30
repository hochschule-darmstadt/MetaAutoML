import json
import logging, asyncio
import os
import time
from concurrent import futures

from requests import request

import Adapter_pb2
import Adapter_pb2_grpc
import grpc
from AdapterUtils import *
from AutoKerasAdapter import AutoKerasAdapter
from JsonUtil import get_config_property
from AdapterBGRPC import *
from grpclib.server import Server

class AdapterService(AdapterServiceBase):
    def __init__(self):
        """
        These variables are used by the ExplainModel function.
        """
        self._automl = None
        self._loaded_training_identifier = None
    async def start_auto_ml(self, start_auto_ml_request: "StartAutoMlRequest") -> AsyncIterator["StartAutoMlResponse"]:
        """
        Execute a new AutoML run.
        """
        try:
            start_time = time.time()
            # saving AutoML configuration JSON
            config = SetupRunNewRunEnvironment(start_auto_ml_request.process_json)

            process = start_automl_process(config)
            async for response in capture_process_output(process, start_time, False):
                yield response
            generate_script(config)
            output_json = zip_script(config)
            #AutoKeras only produces keras based ANN
            library = ":keras_lib"
            model = ":artificial_neural_network"
            test_score, prediction_time = evaluate(config, os.path.join(config["job_folder_location"], get_config_property("job-file-name")), data_loader)
            response = yield get_response(output_json, start_time, test_score, prediction_time, library, model)
            print(f'{get_config_property("adapter-name")} job finished')
            yield response

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while traninh")
                

    async def test_adapter(
        self, test_adapter_request: "TestAdapterRequest"
    ) -> "TestAdapterResponse":
        try:
            config_json = json.loads(test_adapter_request.process_json)
            job_file_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_identifier"],
                                        config_json["training_identifier"],
                                        get_config_property("job-folder-name"),
                                        get_config_property("job-file-name"))

            # saving AutoML configuration JSON
            with open(job_file_location, "w+") as f:
                json.dump(config_json, f)

            test_score, prediction_time, predictions = predict(test_adapter_request.test_data, config_json, job_file_location)
            response = TestAdapterResponse(predictions=predictions)
            response.score = test_score
            response.predictiontime = prediction_time
            return response

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while traninh")

    async def explain_model(
        self, explain_model_request: "ExplainModelRequest"
    ) -> "ExplainModelResponse":
        """
        Function for explaining a model. This returns the prediction probabilities for the data passed within the
        request.data.
        This loads the model and stores it in the adapter object. This is done because SHAP, the explanation module
        accesses this function multiple times and reloading the model every time would add overhead.
        The data transferred is reformatted by SHAP (regarding datatypes and column names). However, the AutoMLs
        struggle with this reformatting so the dataset is loaded separately and the datatypes and column names of the
        transferred data are replaced.
        ---
        param request: Grpc request of type ExplainModelRequest
        param context: Context for correctly handling exceptions
        ---
        return ExplainModelResponse: Grpc response of type ExplainModelResponse containing prediction probabilities
        """
        try:
            config_json = json.loads(explain_model_request.process_json)
            result_folder_location = os.path.join(get_config_property("training-path"),
                                                  config_json["user_identifier"],
                                                  config_json["training_identifier"],
                                                  get_config_property("result-folder-name"))
            # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
            if self._loaded_training_identifier != config_json["training_identifier"]:
                print(f"ExplainModel: Model not already loaded; Loading model")
                with open(result_folder_location + '/model_keras.p', 'rb') as file:
                    self._automl = dill.load(file)
                    # Export model as AutoKeras does not provide the prediction probability.
                    self._automl = self._automl.export_model()
                df, test = data_loader(config_json)
                self._dataframeX, y = prepare_tabular_dataset(df, config_json)
                self._loaded_training_identifier = config_json["training_identifier"]

            # Reassemble dataset with the datatypes and column names from the preprocessed data and the content of the
            # transmitted data.
            df = pd.DataFrame(data=json.loads(request.data), columns=self._dataframeX.columns)
            df = df.astype(dtype=dict(zip(self._dataframeX.columns, self._dataframeX.dtypes.values)))
            # Get prediction probabilities and send them back.
            probabilities = self._automl.predict(np.array(df.values.tolist()))
            # Keras is strange as it does not provide a predict_proba() function to get the class probabilities.
            # Instead, it returns these probabilities (in case there is a binary classification) when calling predict
            # but only as a one dimensional array. Shap however requires the probabilities in the format
            # [[prob class 0, prob class 1], [...]]. So to return the proper format we have to process the results of
            # predict().
            if probabilities.shape[1] == 1:
                probabilities = [[prob[0], 1 - prob[0]] for prob in probabilities.tolist()]
            probabilities = json.dumps(probabilities)
            return Adapter_pb2.ExplainModelResponse(probabilities=probabilities)

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while traninh")

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
        self._loaded_training_identifier = None

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
            #AutoKeras only produces keras based ANN
            library = ":keras_lib"
            model = ":artificial_neural_network"
            test_score, prediction_time = evaluate(config, os.path.join(config["job_folder_location"], get_config_property("job-file-name")), data_loader)
            response = yield from get_response(output_json, start_time, test_score, prediction_time, library, model)
            print(f'{get_config_property("adapter-name")} job finished')
            return response

        except Exception as e:
            return get_except_response(context, e)

    def TestAdapter(self, request, context):
        try:
            config_json = json.loads(request.processJson)
            job_file_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_identifier"],
                                        config_json["training_identifier"],
                                        get_config_property("job-folder-name"),
                                        get_config_property("job-file-name"))

            # saving AutoML configuration JSON
            with open(job_file_location, "w+") as f:
                json.dump(config_json, f)

            test_score, prediction_time, predictions = predict(request.testData, config_json, job_file_location)
            response = Adapter_pb2.TestAdapterResponse(predictions=predictions)
            response.score = test_score
            response.predictiontime = prediction_time
            return response

        except Exception as e:
            return get_except_response(context, e)

    def ExplainModel(self, request, context):
        """
        Function for explaining a model. This returns the prediction probabilities for the data passed within the
        request.data.
        This loads the model and stores it in the adapter object. This is done because SHAP, the explanation module
        accesses this function multiple times and reloading the model every time would add overhead.
        The data transferred is reformatted by SHAP (regarding datatypes and column names). However, the AutoMLs
        struggle with this reformatting so the dataset is loaded separately and the datatypes and column names of the
        transferred data are replaced.
        ---
        param request: Grpc request of type ExplainModelRequest
        param context: Context for correctly handling exceptions
        ---
        return ExplainModelResponse: Grpc response of type ExplainModelResponse containing prediction probabilities
        """
        try:
            config_json = json.loads(request.processJson)
            result_folder_location = os.path.join(get_config_property("training-path"),
                                                  config_json["user_identifier"],
                                                  config_json["training_identifier"],
                                                  get_config_property("result-folder-name"))
            # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
            if self._loaded_training_identifier != config_json["training_identifier"]:
                print(f"ExplainModel: Model not already loaded; Loading model")
                with open(result_folder_location + '/model_keras.p', 'rb') as file:
                    self._automl = dill.load(file)
                    # Export model as AutoKeras does not provide the prediction probability.
                    self._automl = self._automl.export_model()
                df, test = data_loader(config_json)
                self._dataframeX, y = prepare_tabular_dataset(df, config_json)
                self._loaded_training_identifier = config_json["training_identifier"]

            # Reassemble dataset with the datatypes and column names from the preprocessed data and the content of the
            # transmitted data.
            df = pd.DataFrame(data=json.loads(request.data), columns=self._dataframeX.columns)
            df = df.astype(dtype=dict(zip(self._dataframeX.columns, self._dataframeX.dtypes.values)))
            # Get prediction probabilities and send them back.
            probabilities = self._automl.predict(np.array(df.values.tolist()))
            # Keras is strange as it does not provide a predict_proba() function to get the class probabilities.
            # Instead, it returns these probabilities (in case there is a binary classification) when calling predict
            # but only as a one dimensional array. Shap however requires the probabilities in the format
            # [[prob class 0, prob class 1], [...]]. So to return the proper format we have to process the results of
            # predict().
            if probabilities.shape[1] == 1:
                probabilities = [[prob[0], 1 - prob[0]] for prob in probabilities.tolist()]
            probabilities = json.dumps(probabilities)
            return Adapter_pb2.ExplainModelResponse(probabilities=probabilities)

        except Exception as e:
            return get_except_response(context, e)


async def main():
    """
    Boot the gRPC server and wait for incoming connections
    """
    #server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #Adapter_pb2_grpc.add_AdapterServiceServicer_to_server(AdapterServiceServicer(), server)
    #server.add_insecure_port(f'{get_config_property("grpc-server-address")}:{os.getenv("GRPC_SERVER_PORT")}')
    #server.start()

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

    #print(get_config_property("adapter-name") + " started")
    #server.wait_for_termination()
    #with ProcessPoolExecutor(max_workers=40) as executor:
    server = Server([AdapterService()])
    await server.start(get_config_property('grpc-server-address'), os.getenv('GRPC_SERVER_PORT'))
    await server.wait_closed()


if __name__ == '__main__':
    logging.basicConfig()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('done.')
