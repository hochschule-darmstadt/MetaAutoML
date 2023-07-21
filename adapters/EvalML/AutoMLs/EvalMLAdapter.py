import os

from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property

import evalml
from evalml import AutoMLSearch
from evalml import objectives
from evalml import tuners
from evalml import model_family
from evalml.objectives import FraudCost

import pandas as pd
import numpy as np
from predict_time_sources import feature_preparation

from EvalMLWrapper import EvalMLWrapper
import EvalMLParameterConfig as epc

import json
import pickle

# TODO implement
class EvalMLAdapter:
    """Implementation of the AutoML functionality for EvalML

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
        """Start the correct ML task functionality of EvalML"""
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__regression()
            elif self._configuration["configuration"]["task"] == ":text_classification":
                self.__classification()
            elif self._configuration["configuration"]["task"] == ":text_regression":
                self.__regression()
            elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
                self.__time_series_forecasting()

    def __classification(self):
        """Execute the tabular classification task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)

        if len(y.unique()) == 2:
            classification_type = "binary"
            parameters = translate_parameters(":evalml", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), epc.parametersBinary)
        else:
            classification_type =  "multiclass"
            parameters = translate_parameters(":evalml", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), epc.parameters)
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type=classification_type,
                    **parameters,
                    max_batches=3,
                    verbose=False,
                    max_time=self._configuration["configuration"]["runtime_limit"]*60,
                    tuner_class=self.__get_tuner(),
                    allowed_model_families= self.__get_use_approaches(),
                )
        automl.search()
        best_pipeline_tobe_export = automl.best_pipeline
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')
        export_model(EvalMLWrapper(best_pipeline_tobe_export, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')


    def __regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(":evalml", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), epc.parameters)
        problem_type = "REGRESSION"
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type=problem_type,
                    **parameters,
                    max_batches=3,
                    verbose=False,
                    max_time=self._configuration["configuration"]["runtime_limit"]*60,
                    tuner_class=self.__get_tuner(),
                    allowed_model_families= self.__get_use_approaches(),
                )
        automl.search()
        best_pipeline_tobe_export = automl.best_pipeline
        #best_pipeline_tobe_export.save(os.path.join(self._configuration["result_folder_location"], 'evalml.p'))
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')
        export_model(EvalMLWrapper(best_pipeline_tobe_export, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    def __time_series_forecasting(self):
        """Execute the time series forcasting/regression task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        index_column_name = self.__get_index_column()
        #Reset any index and imputation
        self._configuration = reset_index_role(self._configuration)
        X.reset_index(inplace=True)

        parameters = translate_parameters(":evalml", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), epc.parameters)
        self._configuration["forecasting_horizon"] = parameters["forecast_horizon"]
        save_configuration_in_json(self._configuration)

        train, test = data_loader(self._configuration)
        #reload dataset to load changed data

        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)
        X[y.name] = y.values
        #We must persist the training time series to make predictions
        file_path = self._configuration["result_folder_location"]

        file_path = write_tabular_dataset_data(X, file_path, self._configuration, "train.csv")
        X.drop(y.name, axis=1, inplace=True)
        problem_config = {"gap": parameters["gap"], "max_delay": parameters["max_delay"], "forecast_horizon": parameters["forecast_horizon"], "time_index": index_column_name}
        #delete from dic as those parameter are used seperately
        del parameters["max_delay"]
        del parameters["forecast_horizon"]
        del parameters["gap"]
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type="time series regression",
                    max_batches=1,
                    verbose=False,
                    max_time=self._configuration["configuration"]["runtime_limit"]*60,
                    problem_configuration=problem_config,
                    **parameters,
                    tuner_class=self.__get_tuner(),
                    allowed_model_families= self.__get_use_approaches(),
                )
        automl.search()
        best_pipeline_tobe_export = automl.best_pipeline
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')
        export_model(EvalMLWrapper(best_pipeline_tobe_export, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    def __get_index_column(self):
        """get name of index column

        Returns:
            string: column name
        """
        for column, dt in self._configuration['dataset_configuration']['schema'].items():
            if dt.get("role_selected", "") == ":index":
                return column
        return None #

#can be deleted after tuner gets added to parameter config
    def __get_tuner(self):
        """get tuner class
        return none when not setted

        Returns:
            tuner class object: tuner obj
        """
        tuner_dict = {
            ':random' : tuners.RandomSearchTuner ,
            ':grid_search' : tuners.GridSearchTuner ,
            ':skopt' : tuners.SKOptTuner ,
        }
        try:
            return tuner_dict[self._configuration['configuration']['parameters'][':tuner_class_evalml']['values'][0]]
        except:
            print("no tuner param")

        return None


#can be deleted after use approach gets added to parameter config

    def __get_use_approaches(self):
        use_approaches_dict = {
            ':catboost' : model_family.ModelFamily.CATBOOST,
            ':decision_tree' : model_family.ModelFamily.DECISION_TREE,
            ':extra_tree' : model_family.ModelFamily.EXTRA_TREES,
            ':light_gradient_boosting_machine' : model_family.ModelFamily.LIGHTGBM,
            ':linear_regression' : model_family.ModelFamily.LINEAR_MODEL,
            ':random_forest' : model_family.ModelFamily.RANDOM_FOREST,
            ':xgboost' : model_family.ModelFamily.XGBOOST,
            ':auto_regressive_integrated_moving_average' : model_family.ModelFamily.ARIMA,
            ':exponential_smoothing' : model_family.ModelFamily.EXPONENTIAL_SMOOTHING,
            ':k_nearest_neighbor' : model_family.ModelFamily.K_NEIGHBORS,
        }
        try:
            """
            print(self._configuration['configuration']['parameters'][':use_approach'])
            print ( use_approaches_dict[self._configuration['configuration']['parameters'][':use_approach']])
            return use_approaches_dict[self._configuration['configuration']['parameters'][':use_approach']]
    	    """
            res = []
            for i in (self._configuration['configuration']['parameters'][':use_approach']['values']):
                res.append(use_approaches_dict[i])
            print ( res)
            return res
        except:
            print("no use approaches param")

        return None



