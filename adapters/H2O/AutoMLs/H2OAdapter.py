import numpy as np
from AdapterUtils import *
from AdapterTabularUtils import *
import pandas as pd
import json
import os
from JsonUtil import get_config_property
import h2o
from h2o.automl import H2OAutoML
import H2OWrapper
import H2OParameterConfig as h2opc

class h2oAdapter:
    """
    Implementation of the AutoML functionality for H2O
    """
    def __init__(self, configuration: dict):
        """Init a new instance of H2OAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        h2o.init()
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30

    def start(self):
        """Start the correct ML task functionality of H2O"""
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__tabular_classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__tabular_regression()

    def __tabular_classification(self):
        self.df, test = data_loader(self._configuration)
        features, targets = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(":h2o", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), h2opc.parameters)
        parameters.update({"max_trials": self._configuration["configuration"]["runtime_limit"]})
        aml = H2OAutoML(max_runtime_secs = 35, seed = 1, stoppingMetric = "logloss")
        aml.train(y = targets, training_frame = features)


    def __tabular_regression(self):
        self.df, test = data_loader(self._configuration)
        features, targets = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(":h2o", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), h2opc.parameters)
        parameters.update({"max_trials": self._configuration["configuration"]["runtime_limit"]})
        aml = H2OAutoML(max_runtime_secs = 35, seed = 1, stoppingMetric = "deviance")
        aml.train(y = targets, training_frame = features)


    # def __tabular_classification(self):
    #     """Execute the tabular classification task and export the found model"""

    #     self.df, test = data_loader(self._configuration)
        # X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        # parameters = translate_parameters(":h2o", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        # parameters.update({"max_trials": self._configuration["configuration"]["runtime_limit"]})
    #     clf = ak.StructuredDataClassifier(overwrite=True,
    #                                       **parameters,
    #                                       directory=self._configuration["model_folder_location"],
    #                                       seed=42)
    #     H2OAutoML.train()
    #     clf.fit(x=X, y=y, epochs=1, verbose=2)
    #     export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')
    #     export_model(H2OWrapper(clf, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    # def __tabular_regression(self):
    #     """Execute the tabular regression task and export the found model"""

    #     self.df, test = data_loader(self._configuration)
    #     X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
    #     parameters = translate_parameters(":h2o", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
    #     parameters.update({"max_trials": self._configuration["configuration"]["runtime_limit"]})
    #     reg = ak.StructuredDataRegressor(overwrite=True,
    #                                       **parameters,
    #                                      directory=self._configuration["model_folder_location"],
    #                                      seed=42)

    #     reg.fit(x=X, y=y, epochs=1, verbose=2)
    #     export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')
    #     export_model(H2OWrapper(reg, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')
