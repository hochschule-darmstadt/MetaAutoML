import os

from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property


from predict_time_sources import feature_preparation

import json
import pickle
from gama import GamaClassifier,GamaRegressor
from sklearn.datasets import load_breast_cancer

# TODO implement
class GAMAAdapter:
    """Implementation of the AutoML functionality for GAMA

    Args:
        AbstractAdapter (_type_): _description_
    """

    def __init__(self, configuration: dict):
        """Init a new instance of EvalMLAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30

    def start(self):
        """Start the correct ML task functionality of GAMA"""
        print("strt auto ml req")
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__classification()

    def __classification(self):
        """Execute the tabular classification task and export the found model"""
        """
        X, y = load_breast_cancer(return_X_y=True)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, stratify=y, random_state=0
        )

        automl = GamaClassifier(max_total_time=180, store="nothing", n_jobs=1)
        print("Starting `fit` which will take roughly 3 minutes.")
        automl.fit(X_train, y_train)

        label_predictions = automl.predict(X_test)
        probability_predictions = automl.predict_proba(X_test)

        print("accuracy:", accuracy_score(y_test, label_predictions))
        print("log loss:", log_loss(y_test, probability_predictions))
        """
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        set_encoding_for_string_columns(self._configuration, X, y)
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        # TODO: add params
        automl = GamaClassifier(max_total_time=180, store="nothing", n_jobs=1)
        automl.fit(X, y)

        export_model(automl, self._configuration["result_folder_location"], 'GAMA.p')



        return

    def __regression(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        # TODO: add params
        automl = GamaRegressor(max_total_time=180, store="nothing", n_jobs=1)
        automl.fit(X, y)

        export_model(automl, self._configuration["result_folder_location"], 'GAMA.p')


        return



