import autokeras as ak
import numpy as np
from AdapterUtils import data_loader, export_model, prepare_tabular_dataset, get_column_with_largest_amout_of_text, translate_parameters
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
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.task_config)
        clf = ak.StructuredDataClassifier(overwrite=True,
                                          **parameters,
                                          directory=self._configuration["model_folder_location"],
                                          seed=42)

        clf.fit(x=X, y=y, epochs=1)
        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.task_config)
        reg = ak.StructuredDataRegressor(overwrite=True,
                                          **parameters,
                                         directory=self._configuration["model_folder_location"],
                                         seed=42)

        reg.fit(x=X, y=y, epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_classification(self):
        """"Execute image classification task and export the found model"""

        X_train, y_train, X_test, y_test = data_loader(self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.task_config)
        clf = ak.ImageClassifier(overwrite=True,
                                          **parameters,
                                        seed=42,
                                        directory=self._configuration["model_folder_location"])

        #clf.fit(train_data, epochs=self._configuration["runtime_constraints"]["epochs"])
        clf.fit(x = X_train, y = y_train, epochs=1)

        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_regression(self):
        """Execute image regression task and export the found model"""

        X_train, y_train, X_val, y_val = data_loader(self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.task_config)
        reg = ak.ImageRegressor(overwrite=True,
                                          **parameters,
                                        seed=42,
                                        directory=self._configuration["model_folder_location"])

        reg.fit(x = X_train, y = y_train, epochs=1)

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __text_classification(self):
        """Execute text classifiction task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, self._configuration = get_column_with_largest_amout_of_text(self.df, self._configuration)
        X, y = prepare_tabular_dataset(X, self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.task_config)
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
        self.df, test = data_loader(self._configuration)
        X, self._configuration = get_column_with_largest_amout_of_text(self.df, self._configuration)
        X, y = prepare_tabular_dataset(X, self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.task_config)
        reg = ak.TextClassifier(overwrite=True,
                                **parameters,
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        reg.fit(x = np.array(X), y = np.array(y), epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')


    def __time_series_forecasting(self):
        """Execute time series forecasting task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        #TODO convert dataframe to float
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.task_config)
        reg = ak.TimeseriesForecaster(overwrite=True,
                                          **parameters,
                                          lookback=1,
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        X = X.bfill().ffill()  # makes sure there are no missing values
        y = y.bfill().ffill()  # makes sure there are no missing values
        #Loopback must be dividable by batch_size else time seires will crash
        reg.fit(x = X, y = y, epochs=1, batch_size=1)
        model = reg.export_model()
        model.save(os.path.join(self._configuration["result_folder_location"], 'model_keras'), save_format="tf")
        #export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def get_column_with_largest_amout_of_text(self, X: pd.DataFrame):
        """
        Find the column with the most text inside,
        because AutoKeras only supports training with one feature
        Args:
            X (pd.DataFrame): The current X Dataframe

        Returns:
            pd.Dataframe: Returns a pandas Dataframe with the column with the most text inside
        """
        column_names = []
        target = ""
        dict_with_string_length = {}

        #First get only columns that will be used during training
        for column, dt in self._configuration["dataset_configuration"]["schema"].items():
            if dt.get("role_selected", "") == ":ignore" or dt.get("role_selected", "") == ":index" or dt.get("role_selected", "") == ":target":
                continue
            column_names.append(column)

        #Check the used columns by dtype object (== string type) and get mean len to get column with longest text
        for column_name in column_names:
            if(X.dtypes[column_name] == object):
                newlength = X[column_name].str.len().mean()
                dict_with_string_length[column_name] = newlength
        max_value = max(dict_with_string_length, key=dict_with_string_length.get)

        #Remove the to be used text column from the list of used columns and set role ignore as Autokeras can only use one input column for text tasks
        column_names.remove(max_value)
        for column_name in column_names:
            self._configuration["dataset_configuration"]["schema"][column_name]["role_selected"] = ":ignore"

        return X


    def save_configuration_in_json(self):
        """ serialize dataset_configuration to json string and save the the complete configuration in json file
            to habe the right datatypes available for the evaluation
        """
        self._configuration['dataset_configuration'] = json.dumps(self._configuration['dataset_configuration'])
        with open(os.path.join(self._configuration['job_folder_location'], get_config_property("job-file-name")), "w+") as f:
            json.dump(self._configuration, f)
