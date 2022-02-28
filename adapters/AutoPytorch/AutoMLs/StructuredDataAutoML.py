import os
import tempfile as tmp
import warnings

os.environ['JOBLIB_TEMP_FOLDER'] = tmp.gettempdir()
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
from autoPyTorch.api.tabular_classification import TabularClassificationTask
from autoPyTorch.api.tabular_regression import TabularRegressionTask
import pickle

from Utils.JsonUtil import get_config_property
from AutoMLs.predict_time_sources import feature_preparation, DataType, SplitMethod


class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        # set either a runtime limit or an iter limit, preferring runtime over iterations.
        if configuration["runtime_constraints"]["runtime_limit"] > 0:
            self.__time_limit = configuration["runtime_constraints"]["runtime_limit"]
            self.__iter_limit = None
        elif configuration["runtime_constraints"]["max_iter"] > 0:
            self.__time_limit = None
            self.__iter_limit = configuration["runtime_constraints"]["max_iter"]
        else:
            self.__time_limit = 30
            self.__iter_limit = None

        if configuration["metric"] == "" and configuration["task"] == 1:
            # handle empty metric field, 'accuracy' should be the default metric parameter for AutoPytorch classification
            configuration["metric"] = 'accuracy'
        elif configuration["metric"] == "" and configuration["task"] == 2:
            # handle empty metric field, 'r2' should be the default metric parameter for AutoPytorch regression
            configuration["metric"] = 'r2'

        self.__configuration = configuration

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])

        # split training set
        if SplitMethod.SPLIT_METHOD_RANDOM == self.__configuration["test_configuration"]["method"]:
            df = df.sample(random_state=self.__configuration["test_configuration"]["random_state"], frac=1)
        else:
            df = df.iloc[:int(df.shape[0] * self.__configuration["test_configuration"]["split_ratio"])]

        target = self.__configuration["tabular_configuration"]["target"]["target"]
        self.__X = df.drop(target, axis=1)
        self.__y = df[target]

    def __dataset_preparation(self):
        feature_preparation(self.__X, self.__configuration["tabular_configuration"]["features"].items())
        self.__cast_target()

    def __cast_target(self):
        target_dt = self.__configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_CATEGORY:
            self.__y = self.__y.astype('category')
        elif DataType(target_dt) is DataType.DATATYPE_BOOLEAN:
            self.__y = self.__y.astype('bool')
        elif DataType(target_dt) is DataType.DATATYPE_INT:
            self.__y = self.__y.astype('int')
        elif DataType(target_dt) is DataType.DATATYPE_FLOAT:
            self.__y = self.__y.astype('float')

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        output_file = os.path.join(get_config_property('output-path'), 'tmp', "model_pytorch.p")
        with open(output_file, "wb+") as file:
            pickle.dump(model, file)

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        self.__dataset_preparation()

        auto_cls = TabularClassificationTask()
        if self.__time_limit is not None:
            auto_cls.search(
                X_train=self.__X,
                y_train=self.__y,
                optimize_metric=self.__configuration["metric"],
                total_walltime_limit=self.__time_limit
            )
        else:
            auto_cls.search(
                X_train=self.__X,
                y_train=self.__y,
                optimize_metric=self.__configuration["metric"],
                budget_type='epochs',
                max_budget=self.__iter_limit
            )

        self.__export_model(auto_cls)

    def regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        self.__dataset_preparation()
        ############################################################################
        # Build and fit a regressor
        # ==========================
        auto_reg = TabularRegressionTask()

        ############################################################################
        # Search for an ensemble of machine learning algorithms
        # =====================================================
        if self.__time_limit is not None:
            auto_reg.search(
                X_train=self.__X,
                y_train=self.__y,
                optimize_metric=self.__configuration["metric"],
                total_walltime_limit=self.__time_limit
            )
        else:
            auto_reg.search(
                X_train=self.__X,
                y_train=self.__y,
                optimize_metric=self.__configuration["metric"],
                budget_type='epochs',
                max_budget=self.__iter_limit
            )

        self.__export_model(auto_reg)

    def execute_task(self):
        """
        Execute the ML task
        """
        if self.__configuration["task"] == 1:
            self.classification()
        elif self.__configuration["task"] == 2:
            self.regression()
