from AdapterManager import AdapterManager
import json
from AdapterBGRPC import *
from threading import *
import pandas as pd
import numpy as np
import dill
from typing import Tuple
import os
from tpot import TPOTRegressor, TPOTClassifier

class TPOTAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self) -> None:
        """Initialize a new TPOTAdapterManager setting AutoML adapter specific variables
        """
        super(TPOTAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "tpot"

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
        working_dir = config.result_folder_location
        models = list()
        libraries = list()
        with open(os.path.join(working_dir, "model_TPOT.p"), 'rb') as file:
            automl = dill.load(file)
            if config.configuration["task"] == ":tabular_regression":
                for model in automl.steps:
                    if model[0] == "extratreesregressor":
                        libraries.append(":scikit_learn_lib")
                        models.append(":extra_tree")
                    elif model[0] == "gradientboostingregressor":
                        libraries.append(":scikit_learn_lib")
                        models.append(":boosted_decision_tree")
                    elif model[0] == "adaboostregressor":
                        libraries.append(":scikit_learn_lib")
                        models.append(":adaboost")
                    elif model[0] == "decisiontreeregressor":
                        libraries.append(":scikit_learn_lib")
                        models.append(":decision_tree")
                    elif model[0] == "kneighborsregressor":
                        libraries.append(":scikit_learn_lib")
                        models.append(":k_nearest_neighbor")
                    elif model[0] == "lassolarscv":
                        libraries.append(":scikit_learn_lib")
                        models.append(":lasso_regression")
                    elif model[0] == "linearsvr":
                        libraries.append(":scikit_learn_lib")
                        models.append(":linear_svm")
                    elif model[0] == "randomforestregressor":
                        libraries.append(":scikit_learn_lib")
                        models.append(":random_forest")
                    elif model[0] == "ridgecv":
                        libraries.append(":scikit_learn_lib")
                        models.append(":ridge_regression")
                    elif model[0] == "xgbregressor":
                        libraries.append(":xgboost")
                        models.append(":gradient_boosting_tree")
                    elif model[0] == "sgdregressor":
                        libraries.append(":scikit_learn_lib")
                        models.append(":stochastic_gradient_descent")
            if config.configuration["task"] == ":tabular_classification":
                for model in automl.steps:
                    if model[0] == "gaussiannb":
                        libraries.append(":scikit_learn_lib")
                        models.append(":gaussian_naives_bayes")
                    elif model[0] == "bernoullinb":
                        libraries.append(":scikit_learn_lib")
                        models.append(":bernoulli_naive_bayes")
                    elif model[0] == "multinomialnb":
                        libraries.append(":scikit_learn_lib")
                        models.append(":multinominal_naive_bayes")
                    elif model[0] == "decisiontreeclassifier":
                        libraries.append(":scikit_learn_lib")
                        models.append(":decision_tree")
                    elif model[0] == "extratreesclassifier":
                        libraries.append(":scikit_learn_lib")
                        models.append(":extra_tree")
                    elif model[0] == "randomforestclassifier":
                        libraries.append(":scikit_learn_lib")
                        models.append(":random_forest")
                    elif model[0] == "gradientboostingclassifier":
                        libraries.append(":scikit_learn_lib")
                        models.append(":gradient_boosting_tree")
                    elif model[0] == "kneighborsclassifier":
                        libraries.append(":scikit_learn_lib")
                        models.append(":k_nearest_neighbor")
                    elif model[0] == "linearsvc":
                        libraries.append(":scikit_learn_lib")
                        models.append(":linear_svc")
                    elif model[0] == "logisticregression":
                        libraries.append(":scikit_learn_lib")
                        models.append(":logistic_regression")
                    elif model[0] == "xgbclassifier":
                        libraries.append(":xgboost")
                        models.append(":gradient_boosting_tree")
                    elif model[0] == "sgdclassifier":
                        libraries.append(":scikit_learn_lib")
                        models.append(":stochastic_gradient_descent")
                    elif model[0] == "mlpclassifier":
                        libraries.append(":scikit_learn_lib")
                        models.append(":artificial_neural_network")
        return libraries, models

    def _load_model_and_make_probabilities(self, config: "StartAutoMlRequest", result_folder_location: str, dataframe: pd.DataFrame):
        """Must be overwriten! Load the found model, and execute a prediction using the provided data to calculate the probability metric used by the ExplanableAI module inside the controller

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths
            result_folder_location (str): The absolute path leading to the model result location
            dataframe (DataFrame): The dataframe holding the dataset to execute a new prediction on
        """

        if self._loaded_training_id != config["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            with open(result_folder_location + '/model_TPOT.p', 'rb') as file:
                self.__automl = dill.load(file)
            self._loaded_training_id = config["training_id"]
        try:
            probabilities = json.dumps(self.__automl.predict_proba(dataframe).tolist())
        except Exception as e:
            raise(e)
        return probabilities
