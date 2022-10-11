from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property

class AutoKerasAdapterManager(AdapterManager):

    def __init__(self) -> None:
        super(AutoKerasAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None

    def _get_ml_model_and_lib(self):
        return (":keras_lib", ":artificial_neural_network")

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
            if self.__loaded_training_id != config_json["training_id"]:
                print(f"ExplainModel: Model not already loaded; Loading model")
                with open(result_folder_location + '/model_keras.p', 'rb') as file:
                    self.__automl = dill.load(file)
                    # Export model as AutoKeras does not provide the prediction probability.
                    self.__automl = self.__automl.export_model()
                df, test = data_loader(config_json)
                self._dataframeX, y = prepare_tabular_dataset(df, config_json)
                self.__loaded_training_id = config_json["training_id"]

            # Reassemble dataset with the datatypes and column names from the preprocessed data and the content of the
            # transmitted data.
            df = pd.DataFrame(data=json.loads(explain_auto_ml_request.data), columns=self._dataframeX.columns)
            df = df.astype(dtype=dict(zip(self._dataframeX.columns, self._dataframeX.dtypes.values)))
            # Get prediction probabilities and send them back.
            probabilities = self.__automl.predict(np.array(df.values.tolist()))
            # Keras is strange as it does not provide a predict_proba() function to get the class probabilities.
            # Instead, it returns these probabilities (in case there is a binary classification) when calling predict
            # but only as a one dimensional array. Shap however requires the probabilities in the format
            # [[prob class 0, prob class 1], [...]]. So to return the proper format we have to process the results of
            # predict().
            if probabilities.shape[1] == 1:
                probabilities = [[prob[0], 1 - prob[0]] for prob in probabilities.tolist()]
            probabilities = json.dumps(probabilities)
            self.__last_explainable_request = datetime.datetime.now()       #TODO hor to remove old sessions after ending
            return ExplainModelResponse(probabilities=probabilities)

        except Exception as e:
            print(e)
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while traninh")