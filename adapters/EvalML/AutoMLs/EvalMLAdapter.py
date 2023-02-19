import os

from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from AdapterUtils import *
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
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        if len(y.unique()) == 2:
            classification_type = "binary"
        else:
            classification_type =  "multiclass"
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type=classification_type,
                    objective=self.__get_metric(),
                    max_batches=3,
                    verbose=False,
                    tuner_class=self.__get_tuner(),
                    allowed_model_families= self.__get_use_approaches(),
                )
        automl.search()
        automl.describe_pipeline(3)
        best_pipeline_tobe_export = automl.best_pipeline
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')


    def __regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        print(type(X))
        problem_type = "REGRESSION"
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type=problem_type,
                    objective= self.__get_metric(),
                    max_batches=3,
                    verbose=False,
                    tuner_class=self.__get_tuner(),
                    allowed_model_families= self.__get_use_approaches(),
                )
        automl.search()
        automl.describe_pipeline(3)
        best_pipeline_tobe_export = automl.best_pipeline
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')

    def __time_series_forecasting(self):
        """Execute the time series forcasting/regression task and export the found model"""
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        index_column_name = self.__get_index_column()
        #Reset any index and imputation
        self._configuration = reset_index_role(self._configuration)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)

        #We must persist the training time series to make predictions
        file_path = self._configuration["result_folder_location"]
        file_path = write_tabular_dataset_data(self.df, file_path, self._configuration, "train.csv")

        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X.reset_index(inplace=True)

        problem_config = {"gap": 0, "max_delay": 7, "forecast_horizon": 7, "time_index": index_column_name}
        # parameters must be set correctly
        automl = AutoMLSearch(
                    X_train=X,
                    y_train=y,
                    problem_type="time series regression",
                    max_batches=1,
                    verbose=False,
                    problem_configuration=problem_config,
                    objective= self.__get_metric(),
                    tuner_class=self.__get_tuner(),
                    allowed_model_families= self.__get_use_approaches(),
                )
        automl.search()
        best_pipeline_tobe_export = automl.best_pipeline
        export_model(best_pipeline_tobe_export, self._configuration["result_folder_location"], 'evalml.p')

    def __get_index_column(self):
        """get name of index column

        Returns:
            string: column name
        """
        for column, dt in self._configuration['dataset_configuration']['schema'].items():
            if dt.get("role_selected", "") == ":index":
                return column
        return None #

    def __get_metric(self):
        """get accuracy metric (objective) from automl request
            return auto when no metric is provided
        Returns:
            obj of Objective base: metric name
        """
        # TODO: add log loss and matthews_correlation_coefficient for bianry in ontology
        metrics_dict = {
            ':binary_accuracy' : objectives.AccuracyBinary(),
            ':balanced_accuracy' : objectives.BalancedAccuracyMulticlass(),
            ':f_measure' : objectives.F1(),
            ':f_measure_micro' : objectives.F1Micro(),
            ':f_measure_macro' : objectives.F1Macro(),
            ':f_measure_weighted' : objectives.F1Weighted(),
            ':precision' : objectives.Precision(),
            ':precision_macro' : objectives.PrecisionMacro(),
            ':precision_micro' : objectives.PrecisionMicro(),
            ':precision_weighted' : objectives.PrecisionWeighted(),
            ':recall' : objectives.Recall(),
            ':recall_micro' : objectives.RecallMicro(),
            ':recall_macro' : objectives.RecallMacro(),
            ':recall_weighted' : objectives.RecallWeighted(),
            ':area_under_roc_curve' : objectives.AUC(),
            ':area_under_roc_curve_micro' : objectives.AUCMicro(),
            ':area_under_roc_curve_macro' : objectives.AUCMacro(),
            ':gini' : objectives.Gini(),
            ':log_loss' : objectives.LogLossMulticlass(),
            ':matthews_correlation_coefficient' : objectives.MCCMulticlass(),
            ':rooted_mean_squared_error' : objectives.RootMeanSquaredError(),
            ':mean_squared_log_error' : objectives.MeanSquaredLogError(),
            ':rooted_mean_squared_log_error' : objectives.RootMeanSquaredLogError(),
            ':coefficient_of_determination' : objectives.R2(),
            ':mean_absolute_error' : objectives.MAE(),
            ':mean_squared_error' : objectives.MSE(),
            ':median_absolute_error' : objectives.MAE(),
            ':max_error' : objectives.MaxError(),
            ':explained_variance' : objectives.ExpVariance(),
            ':mean_absolute_percentage_error' : objectives.MAPE(),
        }
        try:
            #print(self._configuration['configuration']['parameters'][':metric']['values'][0])
            return metrics_dict[self._configuration['configuration']['parameters'][':metric']['values'][0]]
        except:
            print("no metric param")
        return "auto"

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



