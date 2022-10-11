import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property


class AdapterManager(Thread):

    def __init__(self) -> None:
        super(AdapterManager, self).__init__()
        self.__session_id = ""
        self.__start_auto_ml_running = False
        self.__auto_ml_status_messages = []
        self.__start_auto_ml_request: StartAutoMlRequest = None
        self.__automl = None
        self.__loaded_training_id = None
        self.__on_explain_finished_callback = ""
        self.__on_prediction_finished_callback = ""

    def run(self):
        """
        Listen to the started AutoML process until termination
        ---
        Parameter
        """
        asyncio.run(self.__background_start_auto_ml())
    
    def start_auto_ml(self, start_auto_ml_request: StartAutoMlRequest, session_id):
        self.__start_auto_ml_request = start_auto_ml_request
        self.__session_id = session_id

    def _get_ml_model_and_lib(self):
        return ("", "")

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
            library, model = self._get_ml_model_and_lib()
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
        #Unique to every AutoML, implement in concrete class
        return


    async def predict_model(self, predict_model_request: PredictModelRequest, on_prediction_finished_callback):
        try:
            self.__on_prediction_finished_callback = on_prediction_finished_callback
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
