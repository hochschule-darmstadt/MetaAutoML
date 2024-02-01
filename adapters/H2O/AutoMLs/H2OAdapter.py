import numpy as np
from AdapterUtils import *
from AdapterTabularUtils import *
import pandas as pd
import json
import os
from JsonUtil import get_config_property
from H2OWrapper import H2OWrapper
import H2OParameterConfig as h2opc
import h2o
from h2o.automl import H2OAutoML


class H2OAdapter:
    """
    Implementation of the AutoML functionality for H2O
    Note that h2o only works with h2o-dataframes so they have to be converted before running any jobs.
    Additionally the default export using dill (object as binary) is not working. The h2o import and export functions
    have to be used. They are not shippable across h2o-versions.
    """
    def __init__(self, configuration: dict):
        """Init a new instance of H2OAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        h2o.init()
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"] * 60
        else:
            self._time_limit = 30

    def start(self):
        """Start the correct ML task functionality of H2O"""
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            print("test1")
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()


    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""

        self.df, test = data_loader(self._configuration)
        features, targets = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)

        parameters = translate_parameters(":h2o_automl", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), h2opc.parameters)

        # remove XGBoost if its not in the Selected ML Libaries
        if not(':xgboost_lib' in self._configuration["configuration"].get('selected_ml_libraries', {})) and 'include_algos' in parameters and ('XGBoost' in parameters['include_algos']):
            parameters['include_algos'].remove('XGBoost')


        pandasJoineddf = pd.concat([features, targets], axis=1)
        h2oframe = h2o.H2OFrame(pandasJoineddf)
        h2oframe[targets.name] = h2oframe[targets.name].asfactor() # Stellt sicher, dass H2O Tabular Classification erkennt


        aml = H2OAutoML(max_runtime_secs = self._time_limit, seed = 1, **parameters)
        aml.train(y = targets.name, training_frame = h2oframe)
        # The leader model is stored here
        # View the AutoML Leaderboard
        leaderboard = aml.leaderboard
        best_model = aml.get_best_model()
        #export
        model_path = h2o.save_model(model=best_model, path=self._configuration["result_folder_location"])
        os.rename(model_path, os.path.join(self._configuration["result_folder_location"], 'model_h2o.p'))
        export_model(H2OWrapper(None, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        features, targets = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)

        parameters = translate_parameters(":h2o_automl", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), h2opc.parameters)

        # remove XGBoost if its not in the Selected ML Libaries
        if not(':xgboost_lib' in self._configuration["configuration"].get('selected_ml_libraries', {})) and 'include_algos' in parameters and ('XGBoost' in parameters['include_algos']):
            parameters['include_algos'].remove('XGBoost')


        pandasJoineddf = pd.concat([features, targets], axis=1)
        h2oframe = h2o.H2OFrame(pandasJoineddf)
        h2oframe[targets.name] = h2oframe[targets.name].asnumeric() # Stellt sicher, dass H2O Tabular Regression erkennt


        aml = H2OAutoML(max_runtime_secs = self._time_limit, seed = 1, **parameters)
        aml.train(y = targets.name, training_frame = h2oframe)
        # The leader model is stored here
        # View the AutoML Leaderboard
        leaderboard = aml.leaderboard
        best_model = aml.get_best_model()
        #export
        model_path = h2o.save_model(model=best_model, path=self._configuration["result_folder_location"])
        os.rename(model_path, os.path.join(self._configuration["result_folder_location"], 'model_h2o.p'))
        export_model(H2OWrapper(None, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')
