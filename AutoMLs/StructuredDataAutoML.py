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

from JsonUtil import get_config_property
from enum import Enum, unique


@unique
class DataType(Enum):
    DATATYPE_UNKNOW = 0
    DATATYPE_STRING = 1
    DATATYPE_INT = 2
    DATATYPE_FLOAT = 3
    DATATYPE_CATEGORY = 4
    DATATYPE_BOOLEAN = 5
    DATATYPE_DATETIME = 6
    DATATYPE_IGNORE = 7


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

        self.__configuration = configuration
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        self.__training_data_path = os.path.join(self.__configuration["file_location"], self.__configuration["file_name"])
        print(f"loading file from path {self.__training_data_path}")
        df = pd.read_csv(self.__training_data_path, dtype=object, **self.__configuration["file_configuration"])

        # __X is the entire data without the target column
        self.__X = df.drop(self.__configuration["tabular_configuration"]["target"]["target"], axis=1)
        # __y is only the target column
        self.__y = df[self.__configuration["tabular_configuration"]["target"]["target"]]

    def __dataset_preparation(self):
        for column, dt in self.__configuration["tabular_configuration"]["features"].items():
            if DataType(dt) is DataType.DATATYPE_IGNORE:
                self.__X = self.__X.drop(column, axis=1)
            elif DataType(dt) is DataType.DATATYPE_CATEGORY:
                self.__X[column] = self.__X[column].astype('category')
            elif DataType(dt) is DataType.DATATYPE_BOOLEAN:
                self.__X[column] = self.__X[column].astype('bool')
            elif DataType(dt) is DataType.DATATYPE_INT:
                self.__X[column] = self.__X[column].astype('int')
            elif DataType(dt) is DataType.DATATYPE_FLOAT:
                self.__X[column] = self.__X[column].astype('float')
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
        output_file = os.path.join(get_config_property('output-path'), "model_pytorch.p")
        with open(output_file, "wb") as file:
            pickle.dump(model, file)

        return

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
                optimize_metric='accuracy',
                total_walltime_limit=self.__time_limit
            )
        else:
            auto_cls.search(
                X_train=self.__X,
                y_train=self.__y,
                optimize_metric='accuracy',
                budget_type='epochs',
                max_budget=self.__iter_limit
            )

        ############################################################################
        # Print the final ensemble performance
        # ====================================
        y_pred = auto_cls.predict(self.__X)
        score = auto_cls.score(y_pred, self.__y)
        print(score)
        # Print the final ensemble built by AutoPyTorch
        print(auto_cls.show_models())

        # Print statistics from search
        print(auto_cls.sprint_statistics())

        self.__export_model(auto_cls)

        return

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
                optimize_metric='r2',
                total_walltime_limit=self.__time_limit
            )
        else:
            auto_reg.search(
                X_train=self.__X,
                y_train=self.__y,
                optimize_metric='r2',
                budget_type='epochs',
                max_budget=self.__iter_limit
            )

        ############################################################################
        # Print the final ensemble performance
        # ====================================
        y_pred = auto_reg.predict(self.__X)

        # Rescale the Neural Network predictions into the original target range
        score = auto_reg.score(y_pred, self.__y)

        print(score)
        # Print the final ensemble built by AutoPyTorch
        print(auto_reg.show_models())

        # Print statistics from search
        print(auto_reg.sprint_statistics())

        self.__export_model(auto_reg)

        return

    def execute_task(self):
        """
        Execute the ML task
        """
        if self.__configuration["task"] == 1:
            self.classification()
        elif self.__configuration["task"] == 2:
            self.regression()
