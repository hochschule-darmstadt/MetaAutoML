import autokeras as ak
import numpy as np
from AbstractAdapter import AbstractAdapter
from AdapterUtils import data_loader, export_model, prepare_tabular_dataset
import pandas as pd
from predict_time_sources import DataType
import json
import os
from JsonUtil import get_config_property

class AutoKerasAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for AutoKeras
    """
    def __init__(self, configuration: dict):
        """Init a new instance of AutoKerasAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        super(AutoKerasAdapter, self).__init__(configuration)

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

        clf = ak.StructuredDataClassifier(overwrite=True,
                                          max_trials=3,
                                          # metric=self._configuration['metric'],
                                          directory=self._configuration["model_folder_location"],
                                          seed=42)

        clf.fit(x=X, y=y, epochs=1)
        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        reg = ak.StructuredDataRegressor(overwrite=True,
                                          max_trials=3,
                                         # metric=self._configuration['metric'],
                                         directory=self._configuration["model_folder_location"],
                                         seed=42)

        reg.fit(x=X, y=y, epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_classification(self):
        """"Execute image classification task and export the found model"""

        X_train, y_train, X_test, y_test = data_loader(self._configuration)

        clf = ak.ImageClassifier(overwrite=True,
                                          max_trials=3,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        #clf.fit(train_data, epochs=self._configuration["runtime_constraints"]["epochs"])
        clf.fit(x = X_train, y = y_train, epochs=1)

        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_regression(self):
        """Execute image regression task and export the found model"""

        X_train, y_train, X_val, y_val = data_loader(self._configuration)

        reg = ak.ImageRegressor(overwrite=True,
                                          max_trials=3,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        reg.fit(x = X_train, y = y_train, epochs=1)

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __text_classification(self):
        """Execute text classifiction task and export the found model"""

        self.df, test = data_loader(self._configuration)
        self.get_column_with_largest_amout_of_text(self.df)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        reg = ak.TextClassifier(overwrite=True,
                                # NOTE: bert models will fail with out of memory errors
                                #   even with 32GB GB RAM
                                # the first model is a non-bert transformer
                                max_trials=1,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        reg.fit(x = np.array(X).astype(np.unicode_), y = np.array(y), epochs=1)
        print(self._configuration['dataset_configuration']['column_datatypes'])
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')


    def __text_regression(self):
        """Execute text regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X = self.get_column_with_largest_amout_of_text(X)
        reg = ak.TextClassifier(overwrite=True,
                                          max_trials=3,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        reg.fit(x = np.array(X), y = np.array(y), epochs=1)

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __time_series_forecasting(self):
        """Execute time series forecasting task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        reg = ak.TimeseriesForecaster(overwrite=True,
                                          max_trials=3,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        reg.fit(x = np.array(X), y = np.array(y), epochs=1)

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def get_column_with_largest_amout_of_text(self, df: pd.DataFrame):
        """
        Find the column with the most text inside,
        because AutoKeras only supports training with one feature
        Args:
            X (pd.DataFrame): The current X Dataframe

        Returns:
            pd.Dataframe: Returns a pandas Dataframe with the column with the most text inside
        """
        newdf = df
        X = newdf.drop(self._configuration["configuration"]["target"], axis=1)
        column_names = X.columns
        dict_with_string_length = {}
        for column_name in column_names:
            if(type(X[column_name][1]) == str):
                newlength = X[column_name].str.len().mean()
                dict_with_string_length[column_name] = newlength
        max_value = max(dict_with_string_length, key=dict_with_string_length.get)

        column_names_to_ignore = column_names.drop(max_value)
        for column_name in column_names_to_ignore:
            self._configuration['dataset_configuration']['column_datatypes'][column_name] = 7 #DataType.DATATYPE_IGNORE
    #'C:/Users/pfriehe/Documents/Studium/WiSe2022/PSE/MetaAutoML/adapters/AutoKeras/app-data/training\\fcc66cd1-d166-4d1e-8510-7d93015d83f6\\639f602e684fd91d4fad739f\\63a315022cf2f82c7c7ac41b\\job\\keras-job.json'
        #with open(os.path.join(self._configuration['job_folder_location'],'keras-job.json'), 'w') as outfile:
         #   outfile.write(str(self._configuration))

        with open(os.path.join(self._configuration['job_folder_location'], get_config_property("job-file-name")), "w+") as f:
            json.dump(self._configuration, f)

