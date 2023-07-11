import autokeras as ak
import numpy as np
from AdapterUtils import *
from AdapterTabularUtils import *
import pandas as pd
import json
import os
from JsonUtil import get_config_property
import tensorflow as tf
import keras_tuner
import AutoKerasParameterConfig as akpc


class AutoKerasAdapter:
    """
    Implementation of the AutoML functionality for AutoKeras
    """
    def __init__(self, configuration: dict):
        """Init a new instance of AutoKerasAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30

    def start(self):
        """Start the correct ML task functionality of AutoKeras"""
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__tabular_classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__tabular_regression()
            elif self._configuration["configuration"]["task"] == ":image_classification":
                self.__image_classification()
            elif self._configuration["configuration"]["task"] == ":image_regression":
                self.__image_regression()
            elif self._configuration["configuration"]["task"] == ":text_classification":
                self.__text_classification()
            elif self._configuration["configuration"]["task"] == ":text_regression":
                self.__text_regression()
            elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
                self.__time_series_forecasting()

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        parameters["max_trials"] = self._configuration["configuration"]["runtime_limit"]
        clf = ak.StructuredDataClassifier(overwrite=True,
                                          **parameters,
                                          directory=self._configuration["model_folder_location"],
                                          seed=42)

        clf.fit(x=X, y=y, epochs=1)
        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        parameters["max_trials"] = self._configuration["configuration"]["runtime_limit"]
        reg = ak.StructuredDataRegressor(overwrite=True,
                                          **parameters,
                                         directory=self._configuration["model_folder_location"],
                                         seed=42)

        reg.fit(x=X, y=y, epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_classification(self):
        """"Execute image classification task and export the found model"""

        X_train, y_train = data_loader(self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        parameters["max_trials"] = self._configuration["configuration"]["runtime_limit"]
        clf = ak.ImageClassifier(overwrite=True,
                                        **parameters,
                                        seed=42,
                                        directory=self._configuration["model_folder_location"])

        #clf.fit(train_data, epochs=self._configuration["runtime_constraints"]["epochs"])
        #setting epochs to two because with one an error occurs
        clf.fit(x = X_train, y = y_train, epochs=2)

        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_regression(self):
        """Execute image regression task and export the found model"""

        X_train, y_train = data_loader(self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        parameters["max_trials"] = self._configuration["configuration"]["runtime_limit"]

        reg = ak.ImageRegressor(overwrite=True,
                                          **parameters,
                                        seed=42,
                                        directory=self._configuration["model_folder_location"])

        reg.fit(x = X_train, y = y_train, epochs=1)

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __text_classification(self):
        """Execute text classifiction task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        self._configuration = set_column_with_largest_amout_of_text(X, self._configuration)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        parameters["max_trials"] = self._configuration["configuration"]["runtime_limit"]
        reg = ak.TextClassifier(overwrite=True,
                                # NOTE: bert models will fail with out of memory errors
                                #   even with 32GB GB RAM
                                # the first model is a non-bert transformer
                                **parameters,
                                seed=42,
                                directory=self._configuration["model_folder_location"])


        reg.fit(x = np.array(X).astype(np.unicode_), y = np.array(y), epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')


    def __text_regression(self):
        """Execute text regression task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        self._configuration = set_column_with_largest_amout_of_text(X, self._configuration)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        parameters["max_trials"] = self._configuration["configuration"]["runtime_limit"]
        reg = ak.TextRegressor(overwrite=True,
                                **parameters,
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        reg.fit(x = np.array(X), y = np.array(y), epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')


    def __time_series_forecasting(self):
        """Execute time series forecasting task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)

        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        parameters["max_trials"] = self._configuration["configuration"]["runtime_limit"]
        #oma-ml uses gab as shared parameter which is similar to predict from but has an offset of -1
        # gap = 0 is equal to predict_from  = 1
        parameters["predict_from"] = parameters["predict_from"] + 1
        self._configuration["forecasting_horizon"] = parameters["predict_until"]
        #reload dataset to load changed data
        train, test = data_loader(self._configuration)


        save_configuration_in_json(self._configuration)

        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)

        #TODO convert dataframe to float
        reg = ak.TimeseriesForecaster(overwrite=True,
                                          **parameters,
                                seed=42,
                                directory=self._configuration["model_folder_location"])
        #Loopback must be dividable by batch_size else time seires will crash
        reg.fit(x = X, y = y, epochs=1, batch_size=1)
        model = reg.export_model()
        model.save(os.path.join(self._configuration["result_folder_location"], 'model_keras'), save_format="tf")
        #export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

