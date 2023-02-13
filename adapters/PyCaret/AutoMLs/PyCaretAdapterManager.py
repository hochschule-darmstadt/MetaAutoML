from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
from JsonUtil import get_config_property
import pandas as pd
from typing import Tuple
from pycaret.classification import *
from sklearn.linear_model import *
from sklearn.discriminant_analysis import *
from sklearn.naive_bayes import *
from sklearn.ensemble import *
from xgboost import XGBClassifier
from sklearn.neighbors import *
from sklearn.tree import *
from sklearn.utils.extmath import softmax

class PyCaretAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self) -> None:
        """Initialize a new PyCaretAdapterManager setting AutoML adapter specific variables
        """
        super(PyCaretAdapterManager, self).__init__()
        self.__automl = None
        self.__loaded_training_id = None
        self._adapter_name = "pycaret"

    def _get_ml_model_and_lib(self, config: "StartAutoMlRequest") -> Tuple[str, str]:
        """Get the ML model type and ml library used by the result model

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths

        Returns:
            tuple[str, str]: Tuple returning the ontology IRI of the Ml model type, and ontology IRI of the ML library
        """
        working_dir = config.result_folder_location
        # extract additional information from automl
        automl = load_model(os.path.join(working_dir, 'model_pycaret'))
        if isinstance(automl.named_steps.actual_estimator, RidgeClassifier):
            library = ":scikit_learn_lib"
            model = ":ridge_classifier"
        if isinstance(automl.named_steps.actual_estimator, LinearDiscriminantAnalysis):
            library = ":scikit_learn_lib"
            model = ":linear_discriminant_analysis"
        if isinstance(automl.named_steps.actual_estimator, LogisticRegression):
            library = ":scikit_learn_lib"
            model = ":logistic_regression"
        if isinstance(automl.named_steps.actual_estimator, QuadraticDiscriminantAnalysis):
            library = ":scikit_learn_lib"
            model = ":quadratic_discriminant_analysis"
        if isinstance(automl.named_steps.actual_estimator, GaussianNB):
            library = ":scikit_learn_lib"
            model = ":gaussian_naives_bayes"
        if isinstance(automl.named_steps.actual_estimator, RandomForestClassifier):
            library = ":scikit_learn_lib"
            model = ":random_forest"
        if isinstance(automl.named_steps.actual_estimator, GradientBoostingClassifier):
            library = ":scikit_learn_lib"
            model = ":gradient_boosting_tree"
        if isinstance(automl.named_steps.actual_estimator, XGBClassifier):
            library = ":xgboost"
            model = ":gradient_boosting_tree"
        if isinstance(automl.named_steps.actual_estimator, ExtraTreesClassifier):
            library = ":scikit_learn_lib"
            model = ":extra_tree"
        if isinstance(automl.named_steps.actual_estimator, AdaBoostClassifier):
            library = ":scikit_learn_lib"
            model = ":adaboost"
        if isinstance(automl.named_steps.actual_estimator, KNeighborsClassifier):
            library = ":scikit_learn_lib"
            model = ":k_nearest_neighbor"
        if isinstance(automl.named_steps.actual_estimator, DecisionTreeClassifier):
            library = ":scikit_learn_lib"
            model = ":decision_tree"
        return [library], [model]


    def _load_model_and_make_probabilities(self, config: "StartAutoMlRequest", result_folder_location: str, dataframe: pd.DataFrame):
        """Must be overwriten! Load the found model, and execute a prediction using the provided data to calculate the probability metric used by the ExplanableAI module inside the controller

        Args:
            config (StartAutoMlRequest): extended Start AutoMlRequest holding the training configuration and local training paths
            result_folder_location (str): The absolute path leading to the model result location
            dataframe (DataFrame): The dataframe holding the dataset to execute a new prediction on
        """
        # Check if the requested training is already loaded. If not: Load model and load & prep dataset.
        if self._loaded_training_id != config["training_id"]:
            print(f"ExplainModel: Model not already loaded; Loading model")
            self.__automl = load_model(os.path.join(result_folder_location, "model_pycaret"))
            self._loaded_training_id = config["training_id"]
        # Get prediction probabilities and send them back.
        if isinstance(self.__automl.named_steps.actual_estimator, RidgeClassifier) or isinstance(self.__automl.named_steps.actual_estimator, LogisticRegression):
            #Linear regression models do not have predict_proba method, requires softmax conversion
            d = self.__automl.decision_function(dataframe)
            d_2d = np.c_[-d, d]
            probabilities = softmax(d_2d)
        else:
            probabilities = self.__automl.predict_proba(dataframe)
        probabilities = probabilities.tolist()
        probabilities = json.dumps(probabilities)
        return probabilities
