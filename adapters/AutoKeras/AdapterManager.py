import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property

class AdapterManager(Thread):

    def __init__(self, session_id, on_explain_finished_callback) -> None:
        super(AdapterManager, self).__init__()
        self.__session_id = session_id
        self.__start_auto_ml_running = False
        self.__auto_ml_status_messages = []
        self.__start_auto_ml_request: StartAutoMlRequest = None
        self._automl = None
        self._loaded_training_id = None
        self._on_explain_finished_callback = on_explain_finished_callback

    def run(self):
        """
        Listen to the started AutoML process until termination
        ---
        Parameter
        """
        asyncio.run(self.__background_start_auto_ml())
    
    def start_auto_ml(self, start_auto_ml_request: StartAutoMlRequest):
        self.__start_auto_ml_request = start_auto_ml_request

    async def __background_start_auto_ml(self):
        try:
            self.__start_auto_ml_running = True
            start_time = time.time()
            # saving AutoML configuration JSON
            config = SetupRunNewRunEnvironment(self.__start_auto_ml_request)
            process = start_automl_process(config)
            for response in capture_process_output(process, start_time, False):
                self.__auto_ml_status_messages.append(response)
            generate_script(config)
            output_json = zip_script(config)
            #AutoKeras only produces keras based ANN
            library = ":keras_lib"
            model = ":artificial_neural_network"
            test_score, prediction_time = evaluate(config, os.path.join(config.job_folder_location, get_config_property("job-file-name")), data_loader)
            self.__auto_ml_status_messages.append(get_response(output_json, start_time, test_score, prediction_time, library, model))
            print(f'{get_config_property("adapter-name")} job finished')
            self.__start_auto_ml_running = False

        except Exception as e:
            self.__start_auto_ml_running = False
            self.__auto_ml_status_messages.append(get_except_response(e))


    def get_auto_ml_status(self):
        if (len(self.__auto_ml_status_messages) == 0) and self.__start_auto_ml_running == False:
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Adapter session {self.__session_id} endded and no messages are left!")
        if (len(self.__auto_ml_status_messages) == 0) and self.__start_auto_ml_running == True:
            response = GetAutoMlStatusResponse()
            response.return_code = AdapterReturnCode.ADAPTER_RETURN_CODE_PENDING
            return response
        len(self.__auto_ml_status_messages)
        return self.__auto_ml_status_messages.pop(0)


    async def explain_model(self, explain_auto_ml_request: "ExplainModelRequest"):
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
            config_json = json.loads(explain_auto_ml_request.process_json)
            result_folder_location = os.path.join(get_config_property("training-path"),
                                                  config_json["user_id"],
                                                    config_json["dataset_id"],
                                                  config_json["training_id"],
                                                  get_config_property("result-folder-name"))
            # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
            if self._loaded_training_id != config_json["training_id"]:
                print(f"ExplainModel: Model not already loaded; Loading model")
                with open(result_folder_location + '/model_keras.p', 'rb') as file:
                    self._automl = dill.load(file)
                    # Export model as AutoKeras does not provide the prediction probability.
                    self._automl = self._automl.export_model()
                df, test = data_loader(config_json)
                self._dataframeX, y = prepare_tabular_dataset(df, config_json)
                self._loaded_training_id = config_json["training_id"]

            # Reassemble dataset with the datatypes and column names from the preprocessed data and the content of the
            # transmitted data.
            df = pd.DataFrame(data=json.loads(explain_auto_ml_request.data), columns=self._dataframeX.columns)
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
            return ExplainModelResponse(probabilities=probabilities)

        except Exception as e:
            print(e)
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while traninh")


    async def predict_model(self, predict_model_request: PredictModelRequest):
        try:
            config_json = json.loads(predict_model_request.process_json)
            job_file_location = os.path.join(get_config_property("training-path"),
                                        config_json["user_id"],
                                        config_json["dataset_id"],
                                        config_json["training_id"],
                                        get_config_property("job-folder-name"),
                                        get_config_property("job-file-name"))

            # saving AutoML configuration JSON
            with open(job_file_location, "w+") as f:
                json.dump(config_json, f)

            prediction_time, result_path = predict(config_json, job_file_location, "autokeras")
            response = PredictModelResponse()
            response.result_path = result_path
            response.predictiontime = prediction_time
            return response

        except Exception as e:
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while traninh")
