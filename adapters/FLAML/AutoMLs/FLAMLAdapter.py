import os
from AdapterUtils import *
from AdapterTabularUtils import *
from explainerdashboard import ClassifierExplainer, RegressionExplainer, ExplainerDashboard
from explainerdashboard import ClassifierExplainer, RegressionExplainer, ExplainerDashboard
from flaml import AutoML
import numpy as np
from sklearn.impute import SimpleImputer
import pandas as pd
import json
from JsonUtil import get_config_property
import FLAMLParameterConfig as fpc

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
        elif self._configuration["configuration"]["task"] == ":text_classification":
            self.__text_classification()

    def __generate_settings(self) -> dict:
        """Generate the settings dictionary for FLAML

        Returns:
            dict: Settings configuration for FLAML
        """
        automl_settings = {"log_file_name": 'flaml.log'}
        automl_settings.update({"time_budget": self._configuration["configuration"]["runtime_limit"] * 60})

        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), fpc.task_config)
        if parameters.get('estimator_list', None) != None:
            if parameters['estimator_list'] == ['auto']:
                parameters['estimator_list'] = 'auto'
        automl_settings.update(parameters)



        return automl_settings

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X, y = replace_forbidden_json_utf8_characters(X, y)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "task": 'classification',
            "ensemble": True,
            "log_file_name": self._log_file_path
        })

        X[y.name] = y.values
        automl.fit(dataframe=X, label=y.name, **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')
        self.__create_explainer_dashboard(X, y)

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X, y = replace_forbidden_json_utf8_characters(X, y)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "task": 'regression',
            "ensemble": True,
            "log_file_name": self._log_file_path
        })

        X[y.name] = y.values
        automl.fit(dataframe=X, label=y.name, **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')


    def __time_series_forecasting(self):
        """Execute the tabular classification task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Reset any index and imputation
        self._configuration = reset_index_role(self._configuration)
        X.reset_index(inplace = True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)

        automl_settings = self.__generate_settings()

        self._configuration["forecasting_horizon"] = automl_settings["period"]
        save_configuration_in_json(self._configuration)
        
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        #TODO ensure ts first column is datetime
        automl = AutoML()
        
        automl_settings.update({
            "task": 'ts_forecast',
            "ensemble": True,
            "log_file_name": self._log_file_path,
            "period": 12,
            "eval_method": "holdout"
        })
        #X.reset_index(inplace=True)
        #X = X.bfill().ffill()  # makes sure there are no missing values
        automl.fit(X_train=X, y_train=y, **automl_settings)

        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')

    def __text_classification(self):
        """Execute the tabular classification task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Reset any index and imputation
        self._configuration = set_column_with_largest_amout_of_text(X, self._configuration)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        X, y = replace_forbidden_json_utf8_characters(X, y)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "task": 'seq-classification',
            "ensemble": True,
            "fit_kwargs_by_estimator": {
                "transformer": {
                    "output_dir": self._configuration["model_folder_location"],   # setting the output directory
                }
            },
            "log_file_name": self._log_file_path,
            "fp16": False
        })

        X[y.name] = y.values
        automl.fit(dataframe=X, label=y.name, **automl_settings)

        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')

    def __create_explainer_dashboard(self):
        """Creates the ExplainerDashboard based on the generated model""" 
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(test, self._configuration)

        with open(os.path.join(self._configuration["result_folder_location"], "model_flaml.p"), 'rb') as file:
            model = dill.load(file)

        if self._configuration["configuration"]["task"] == ":tabular_classification" or self._configuration["configuration"]["task"] == ":text_classification" :
            dashboard = ExplainerDashboard(ClassifierExplainer(model, X, y))
        else :
            dashboard = ExplainerDashboard(RegressionExplainer(model, X, y))

        dash_path = os.path.abspath(os.path.join(self._configuration["result_folder_location"], os.pardir))
        os.makedirs(os.path.join(dash_path, "dashboard"), exist_ok=True)
        dash_path = os.path.join(dash_path, "dashboard")

        dashboard.save_html(os.path.join(dash_path, "binary_dashboard.html"))
        dashboard.explainer.dump(os.path.join(dash_path, "binary_dashboard.dill"))