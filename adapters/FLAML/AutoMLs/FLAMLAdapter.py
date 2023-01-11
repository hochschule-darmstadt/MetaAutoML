import os

from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from flaml import AutoML
import numpy as np
from sklearn.impute import SimpleImputer

class FLAMLAdapter:
    """
    Implementation of the AutoML functionality for FLAML
    """

    def __init__(self, configuration: dict):
        """Init a new instance of FLAMLAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30
        self._result_path = configuration["model_folder_location"]
        self._log_file_path = os.path.join(self._result_path, "flaml.log")

    def start(self):
        """Start the correct ML task functionality of FLAML"""
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()
        elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
            self.__time_series_forecasting()

    def __generate_settings(self) -> dict:
        """Generate the settings dictionary for FLAML

        Returns:
            dict: Settings configuration for FLAML
        """
        automl_settings = {"log_file_name": 'flaml.log'}
        if self._configuration["configuration"]["runtime_limit"] != 0:
            automl_settings.update({"time_budget": self._configuration["configuration"]["runtime_limit"]})
        return automl_settings

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            #"metric": self._configuration["configuration"]["metric"] if self._configuration["configuration"]["metric"] != "" else 'accuracy',
            "metric": 'accuracy',
            "task": 'classification',
            "log_file_name": self._log_file_path
        })

        automl.fit(X_train=np.array(X), y_train=np.array(y), **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            #"metric": self._configuration["configuration"]["metric"] if self._configuration["configuration"]["metric"] != "" else 'accuracy',
            "metric": 'mse',
            "task": 'regression',
            "log_file_name": self._log_file_path
        })

        automl.fit(X_train=np.array(X), y_train=np.array(y), **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')


    def __time_series_forecasting(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        #TODO ensure ts first column is datetime
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            #"metric": self._configuration["configuration"]["metric"] if self._configuration["configuration"]["metric"] != "" else 'accuracy',
            "metric": 'mape',
            "task": 'ts_forecast',
            "log_file_name": self._log_file_path,
            "period": 1,
            "eval_method": "holdout"
        })
        x_shape = X.shape[-1]
        y_shape = y.shape[-1]
        automl.fit(X_train=X, y_train=y, **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')
