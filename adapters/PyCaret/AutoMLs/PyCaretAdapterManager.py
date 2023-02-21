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
from sklearn.gaussian_process import *
from sklearn.svm import *
from xgboost import *
from sklearn.neighbors import *
from sklearn.tree import *
from sklearn.neural_network import *
from pycaret.internal.tunable import *
from catboost import *
from lightgbm import *
from pycaret.internal.tunable import TunableMLPRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.utils.extmath import softmax
from lightgbm import LGBMClassifier

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
        if isinstance(automl.named_steps.trained_model, LogisticRegression):
            library = ":scikit_learn_lib"
            model = ":logistic_regression"
        if isinstance(automl.named_steps.trained_model, KNeighborsClassifier):
            library = ":scikit_learn_lib"
            model = ":k_nearest_neighbor"
        if isinstance(automl.named_steps.trained_model, GaussianNB):
            library = ":scikit_learn_lib"
            model = ":gaussian_naives_bayes"
        if isinstance(automl.named_steps.trained_model, DecisionTreeClassifier):
            library = ":scikit_learn_lib"
            model = ":decision_tree"
        if isinstance(automl.named_steps.trained_model, SGDClassifier):
            library = ":scikit_learn_lib"
            model = ":support_vector_machine"
        if isinstance(automl.named_steps.trained_model, SVC):
            library = ":scikit_learn_lib"
            model = ":support_vector_machine"
        if isinstance(automl.named_steps.trained_model, GaussianProcessClassifier):
            library = ":scikit_learn_lib"
            model = ":gaussian_process"
        if isinstance(automl.named_steps.trained_model, MLPClassifier):
            library = ":scikit_learn_lib"
            model = ":artificial_neural_network"
        if isinstance(automl.named_steps.trained_model, TunableMLPClassifier):
            library = ":scikit_learn_lib"
            model = ":artificial_neural_network"
        if isinstance(automl.named_steps.trained_model, RidgeClassifier):
            library = ":scikit_learn_lib"
            model = ":ridge_classifier"
        if isinstance(automl.named_steps.trained_model, RandomForestClassifier):
            library = ":scikit_learn_lib"
            model = ":random_forest"
        if isinstance(automl.named_steps.trained_model, QuadraticDiscriminantAnalysis):
            library = ":scikit_learn_lib"
            model = ":quadratic_discriminant_analysis"
        if isinstance(automl.named_steps.trained_model, AdaBoostClassifier):
            library = ":scikit_learn_lib"
            model = ":adaboost"
        if isinstance(automl.named_steps.trained_model, GradientBoostingClassifier):
            library = ":scikit_learn_lib"
            model = ":gradient_boosting_tree"
        if isinstance(automl.named_steps.trained_model, LinearDiscriminantAnalysis):
            library = ":scikit_learn_lib"
            model = ":linear_discriminant_analysis"
        if isinstance(automl.named_steps.trained_model, ExtraTreesClassifier):
            library = ":scikit_learn_lib"
            model = ":extra_tree"
        if isinstance(automl.named_steps.trained_model, XGBClassifier):
            library = ":xgboost"
            model = ":gradient_boosting_tree"
        if isinstance(automl.named_steps.trained_model, LGBMClassifier):
            library = ":lightgbm_lib"
            model = ":light_gradient_boosting_machine"
        if isinstance(automl.named_steps.trained_model, CatBoostClassifier):
            library = ":catboost_lib"
            model = ":catboost"
        if isinstance(automl.named_steps.trained_model, Lasso):
            library = ":scikit_learn_lib"
            model = ":linear_regression"
        if isinstance(automl.named_steps.trained_model, Ridge):
            library = ":scikit_learn_lib"
            model = ":kernel_ridge_regression"
        if isinstance(automl.named_steps.trained_model, ElasticNet):
            library = ":scikit_learn_lib"
            model = ":linear_regression"
        if isinstance(automl.named_steps.trained_model, Lars):
            library = ":scikit_learn_lib"
            model = ":lasso_regression"
        if isinstance(automl.named_steps.trained_model, LassoLars):
            library = ":scikit_learn_lib"
            model = ":lasso_regression"
        if isinstance(automl.named_steps.trained_model, OrthogonalMatchingPursuit):
            library = ":scikit_learn_lib"
            model = ":orthogonal_matching_pursuit"
        if isinstance(automl.named_steps.trained_model, BayesianRidge):
            library = ":scikit_learn_lib"
            model = ":bayesian_linear_regression"
        if isinstance(automl.named_steps.trained_model, ARDRegression):
            library = ":scikit_learn_lib"
            model = ":bayesian_linear_regression"
        if isinstance(automl.named_steps.trained_model, PassiveAggressiveRegressor):
            library = ":scikit_learn_lib"
            model = ":passive_aggressive"
        if isinstance(automl.named_steps.trained_model, RANSACRegressor):
            library = ":scikit_learn_lib"
            model = ":random_sample_consensus"
        if isinstance(automl.named_steps.trained_model, TheilSenRegressor):
            library = ":scikit_learn_lib"
            model = ":multivariate_regression"
        if isinstance(automl.named_steps.trained_model, HuberRegressor):
            library = ":scikit_learn_lib"
            model = ":linear_regression"
        if isinstance(automl.named_steps.trained_model, KernelRidge):
            library = ":scikit_learn_lib"
            model = ":kernel_ridge_regression"
        if isinstance(automl.named_steps.trained_model, SVR):
            library = ":scikit_learn_lib"
            model = ":support_vector_regression"
        if isinstance(automl.named_steps.trained_model, KNeighborsRegressor):
            library = ":scikit_learn_lib"
            model = ":k_nearest_neighbor"
        if isinstance(automl.named_steps.trained_model, DecisionTreeRegressor):
            library = ":scikit_learn_lib"
            model = ":decision_tree"
        if isinstance(automl.named_steps.trained_model, RandomForestRegressor):
            library = ":scikit_learn_lib"
            model = ":random_forest"
        if isinstance(automl.named_steps.trained_model, ExtraTreeRegressor):
            library = ":scikit_learn_lib"
            model = ":extra_tree"
        if isinstance(automl.named_steps.trained_model, AdaBoostRegressor):
            library = ":scikit_learn_lib"
            model = ":adaboost"
        if isinstance(automl.named_steps.trained_model, GradientBoostingRegressor):
            library = ":scikit_learn_lib"
            model = ":gradient_boosting_tree"
        if isinstance(automl.named_steps.trained_model, MLPRegressor):
            library = ":Lightgbm_lib"
            model = ":artificial_neural_network"
        if isinstance(automl.named_steps.trained_model, TunableMLPRegressor):
            library = ":scikit_learn_lib"
            model = ":artificial_neural_network"
        if isinstance(automl.named_steps.trained_model, XGBRegressor):
            library = ":xgboost"
            model = ":gradient_boosting_tree"
        if isinstance(automl.named_steps.trained_model, LGBMRegressor):
            library = ":Lightgbm_lib"
            model = ":light_gradient_boosting_machine"
        if isinstance(automl.named_steps.trained_model, CatBoostRegressor):
            library = ":catboost_lib"
            model = ":catboost"
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
        if isinstance(self.__automl.named_steps.trained_model, RidgeClassifier) or isinstance(self.__automl.named_steps.trained_model, LogisticRegression):
            #Linear regression models do not have predict_proba method, requires softmax conversion
            d = self.__automl.decision_function(dataframe)
            d_2d = np.c_[-d, d]
            probabilities = softmax(d_2d)
        else:
            probabilities = self.__automl.predict_proba(dataframe)
        probabilities = probabilities.tolist()
        probabilities = json.dumps(probabilities)
        return probabilities
