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


class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, json: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        self.__time_limit = 60
        self.__json = json
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        self.__training_data_path = os.path \
            .join(self.__json["file_location"]
                  , self.__json["file_name"])
        df = pd.read_csv(self.__training_data_path, dtype=object, quotechar='\"')

        # __X is the entire data without the target column
        self.__X = df.drop(self.__json["configuration"]["target"], axis=1)
        # __y is only the target column
        self.__y = df[self.__json["configuration"]["target"]]

        return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open(f"templates/output/autopytorch-model.p", "wb") as file:
            pickle.dump(model, file)

        return

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()

        auto_cls = TabularClassificationTask()
        auto_cls.search(
            X_train=self.__X,
            y_train=self.__y,
            optimize_metric='accuracy',
            total_walltime_limit=self.__time_limit,
            func_eval_time_limit_secs=50
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

        ############################################################################
        # Build and fit a regressor
        # ==========================
        auto_reg = TabularRegressionTask()

        ############################################################################
        # Search for an ensemble of machine learning algorithms
        # =====================================================
        auto_reg.search(
            X_train=self.__X,
            y_train=self.__y,
            optimize_metric='r2',
            total_walltime_limit=self.__time_limit,
            func_eval_time_limit_secs=50,
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
