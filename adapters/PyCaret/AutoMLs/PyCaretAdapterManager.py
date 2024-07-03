from AdapterManager import AdapterManager
import json
import os
import time, asyncio
from AdapterUtils import *
from AdapterBGRPC import *
from threading import *
import pandas as pd
from typing import Tuple
from pycaret.classification import *
from sklearn.linear_model import *
from sklearn.discriminant_analysis import *
from sklearn.naive_bayes import *
from sklearn.ensemble import *
from sklearn.gaussian_process import *
from sklearn.svm import *
from sklearn.neighbors import *
from sklearn.tree import *
from sklearn.neural_network import *
from pycaret.internal.tunable import *
from lightgbm import *
from pycaret.internal.tunable import TunableMLPRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.utils.extmath import softmax
from lightgbm import LGBMClassifier

from ThreadLock import ThreadLock

def get_lib_model_names(instance):
    if isinstance(instance, LogisticRegression):
        return ":scikit_learn_lib", ":logistic_regression"
    if isinstance(instance, KNeighborsClassifier):
        return ":scikit_learn_lib", ":k_nearest_neighbor"
    if isinstance(instance, GaussianNB):
        return ":scikit_learn_lib", ":gaussian_naives_bayes"
    if isinstance(instance, DecisionTreeClassifier):
        return ":scikit_learn_lib", ":decision_tree"
    if isinstance(instance, SGDClassifier):
        return ":scikit_learn_lib", ":support_vector_machine"
    if isinstance(instance, SVC):
        return ":scikit_learn_lib", ":support_vector_machine"
    if isinstance(instance, GaussianProcessClassifier):
        return ":scikit_learn_lib", ":gaussian_process"
    if isinstance(instance, MLPClassifier):
        return ":scikit_learn_lib", ":artificial_neural_network"
    if isinstance(instance, TunableMLPClassifier):
        return ":scikit_learn_lib", ":artificial_neural_network"
    if isinstance(instance, RidgeClassifier):
        return ":scikit_learn_lib", ":ridge_classifier"
    if isinstance(instance, RandomForestClassifier):
        return ":scikit_learn_lib", ":random_forest"
    if isinstance(instance, QuadraticDiscriminantAnalysis):
        return ":scikit_learn_lib", ":quadratic_discriminant_analysis"
    if isinstance(instance, AdaBoostClassifier):
        return ":scikit_learn_lib", ":adaboost"
    if isinstance(instance, GradientBoostingClassifier):
        return ":scikit_learn_lib", ":gradient_boosting_tree"
    if isinstance(instance, LinearDiscriminantAnalysis):
        return ":scikit_learn_lib", ":linear_discriminant_analysis"
    if isinstance(instance, ExtraTreesClassifier):
        return ":scikit_learn_lib", ":extra_tree"
    #if isinstance(instance, XGBClassifier):
    #    return ":xgboost", ":gradient_boosting_tree"
    if isinstance(instance, LGBMClassifier):
        return ":lightgbm_lib", ":light_gradient_boosting_machine"
    #if isinstance(instance, CatBoostClassifier):
    #    return ":catboost_lib", ":catboost"
    if isinstance(instance, Lasso):
        return ":scikit_learn_lib", ":linear_regression"
    if isinstance(instance, Ridge):
        return ":scikit_learn_lib", ":kernel_ridge_regression"
    if isinstance(instance, ElasticNet):
        return ":scikit_learn_lib", ":linear_regression"
    if isinstance(instance, Lars):
        return ":scikit_learn_lib", ":lasso_regression"
    if isinstance(instance, LassoLars):
        return ":scikit_learn_lib", ":lasso_regression"
    if isinstance(instance, OrthogonalMatchingPursuit):
        return ":scikit_learn_lib", ":orthogonal_matching_pursuit"
    if isinstance(instance, BayesianRidge):
        return ":scikit_learn_lib", ":bayesian_linear_regression"
    if isinstance(instance, ARDRegression):
        return ":scikit_learn_lib", ":bayesian_linear_regression"
    if isinstance(instance, PassiveAggressiveRegressor):
        return ":scikit_learn_lib", ":passive_aggressive"
    if isinstance(instance, RANSACRegressor):
        return ":scikit_learn_lib", ":random_sample_consensus"
    if isinstance(instance, TheilSenRegressor):
        return ":scikit_learn_lib", ":multivariate_regression"
    if isinstance(instance, HuberRegressor):
        return ":scikit_learn_lib", ":linear_regression"
    if isinstance(instance, KernelRidge):
        return ":scikit_learn_lib", ":kernel_ridge_regression"
    if isinstance(instance, SVR):
        return ":scikit_learn_lib", ":support_vector_regression"
    if isinstance(instance, KNeighborsRegressor):
        return ":scikit_learn_lib", ":k_nearest_neighbor"
    if isinstance(instance, DecisionTreeRegressor):
        return ":scikit_learn_lib", ":decision_tree"
    if isinstance(instance, RandomForestRegressor):
        return ":scikit_learn_lib", ":random_forest"
    if isinstance(instance, ExtraTreeRegressor):
        return ":scikit_learn_lib", ":extra_tree"
    if isinstance(instance, AdaBoostRegressor):
        return ":scikit_learn_lib", ":adaboost"
    if isinstance(instance, GradientBoostingRegressor):
        return ":scikit_learn_lib", ":gradient_boosting_tree"
    if isinstance(instance, MLPRegressor):
        return ":Lightgbm_lib", ":artificial_neural_network"
    if isinstance(instance, TunableMLPRegressor):
        return ":scikit_learn_lib", ":artificial_neural_network"
    #if isinstance(instance, XGBRegressor):
    #    return ":xgboost", ":gradient_boosting_tree"
    if isinstance(instance, LGBMRegressor):
        return ":Lightgbm_lib", ":light_gradient_boosting_machine"
    #if isinstance(instance, CatBoostRegressor):
    #    return ":catboost_lib", ":catboost"
    else:
        return ":scikit_learn_lib", ":logistic_regression"


class PyCaretAdapterManager(AdapterManager):
    """The AutoML solution specific functionality implementation of the AdapterManager class

    Args:
        AdapterManager (AdapterManager): The base class providing the shared functionality for all adapters
    """

    def __init__(self, lock: ThreadLock) -> None:
        """Initialize a new PyCaretAdapterManager setting AutoML adapter specific variables
        """
        super(PyCaretAdapterManager, self).__init__(lock)
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
        libraries = []
        models = []
        working_dir = config.result_folder_location
        # extract additional information from automl
        automl = load_model(os.path.join(working_dir, 'model_pycaret'))
        try:
            lib, model = get_lib_model_names(automl.named_steps.trained_model)
        except:
            lib, model = get_lib_model_names(automl)
        libraries.append(lib)
        models.append(model)
        return libraries, models


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
        if isinstance(self.__automl, RidgeClassifier) or isinstance(self.__automl, LogisticRegression):
            #Linear regression models do not have predict_proba method, requires softmax conversion
            d = self.__automl.decision_function(dataframe)
            d_2d = np.c_[-d, d]
            probabilities = softmax(d_2d)
        else:
            probabilities = self.__automl.predict_proba(dataframe)
        probabilities = probabilities.tolist()
        probabilities = json.dumps(probabilities)
        return probabilities
