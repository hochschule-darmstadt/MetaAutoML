import os
import tempfile as tmp
import warnings

os.environ['JOBLIB_TEMP_FOLDER'] = tmp.gettempdir()
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

import pickle

import pandas as pd
from AbstractAdapter import AbstractAdapter
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from autoPyTorch.api.tabular_classification import TabularClassificationTask
from autoPyTorch.api.tabular_regression import TabularRegressionTask
from JsonUtil import get_config_property
from predict_time_sources import DataType, SplitMethod, feature_preparation


class AutoPytorchAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of TabularDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        # set either a runtime limit or an iter limit, preferring runtime over iterations.
        
        super().__init__(configuration)
        
        if self._configuration["runtime_constraints"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["runtime_constraints"]["runtime_limit"]
            self._iter_limit = None
        elif self._configuration["runtime_constraints"]["max_iter"] > 0:
            self._time_limit = None
            self._iter_limit = self._configuration["runtime_constraints"]["max_iter"]
        else:
            self._time_limit = 30
            self._iter_limit = None

        if self._configuration["metric"] == "" and self._configuration["task"] == 1:
            # handle empty metric field, 'accuracy' should be the default metric parameter for AutoPytorch classification
            self._configuration["metric"] = 'accuracy'
        elif self._configuration["metric"] == "" and self._configuration["task"] == 2:
            # handle empty metric field, 'r2' should be the default metric parameter for AutoPytorch regression
            self._configuration["metric"] = 'r2'
        self._result_path = os.path.join(get_config_property("output-path"), self._configuration["session_id"])

    def __tabular_classification(self):
        """
        Execute the classification task
        """
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        auto_cls = TabularClassificationTask()
        if self._time_limit is not None:
            auto_cls.search(
                X_train=X,
                y_train=y,
                optimize_metric=self._configuration["metric"],
                total_walltime_limit=self._time_limit
            )
        else:
            auto_cls.search(
                X_train=X,
                y_train=y,
                optimize_metric=self._configuration["metric"],
                budget_type='epochs',
                max_budget=self._iter_limit
            )

        export_model(auto_cls, self._configuration["session_id"], "model_pytorch.p")

    def __tabular_regression(self):
        """
        Execute the regression task
        """
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        ############################################################################
        # Build and fit a regressor
        # ==========================
        auto_reg = TabularRegressionTask()

        ############################################################################
        # Search for an ensemble of machine learning algorithms
        # =====================================================
        if self._time_limit is not None:
            auto_reg.search(
                X_train=X,
                y_train=y,
                optimize_metric=self._configuration["metric"],
                total_walltime_limit=self._time_limit
            )
        else:
            auto_reg.search(
                X_train=X,
                y_train=y,
                optimize_metric=self._configuration["metric"],
                budget_type='epochs',
                max_budget=self._iter_limit
            )

        export_model(auto_reg, self._configuration["session_id"], "model_pytorch.p")

    def start(self):
        """
        Execute the ML task
        """
        if self._configuration["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["task"] == ":tabular_regression":
            self.__tabular_regression()
