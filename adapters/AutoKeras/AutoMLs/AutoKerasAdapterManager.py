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
        self._adapter_name = "autokeras"

    def _get_ml_model_and_lib(self, config):
        return (":keras_lib", ":artificial_neural_network")

    def _load_model_and_make_probabilities(self, config_json, result_folder_location, dataframe):
        # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
        if self._loaded_training_id != config_json["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            with open(result_folder_location + '/model_keras.p', 'rb') as file:
                self.__automl = dill.load(file)
                # Export model as AutoKeras does not provide the prediction probability.
                self.__automl = self.__automl.export_model()
            self._loaded_training_id = config_json["training_id"]
            # Get prediction probabilities and send them back.
        probabilities = self.__automl.predict(np.array(dataframe.values.tolist()))
        # Keras is strange as it does not provide a predict_proba() function to get the class probabilities.
        # Instead, it returns these probabilities (in case there is a binary classification) when calling predict
        # but only as a one dimensional array. Shap however requires the probabilities in the format
        # [[prob class 0, prob class 1], [...]]. So to return the proper format we have to process the results of
        # predict().
        if probabilities.shape[1] == 1:
            probabilities = [[1 - prob[0], prob[0]] for prob in probabilities.tolist()]
        probabilities = json.dumps(probabilities)
        return probabilities
