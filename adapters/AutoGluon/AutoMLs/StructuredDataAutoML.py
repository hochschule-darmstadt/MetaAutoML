import os
import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor
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
        self.__configuration = configuration
        self.target = self.__configuration["tabular_configuration"]["target"]["target"]

        # set default values
        if self.__configuration["runtime_constraints"]["runtime_limit"] == 0:
            self.__configuration["runtime_constraints"]["runtime_limit"] = 20

        self.__output_path = os.path.join(get_config_property('output-path'),
                                          'tmp',
                                          'model_gluon.gluon')

    def __read_training_data(self):
        """
        Read the training dataset from disk
        In case of AutoGluon only provide the training file path
        """
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])

        # split training set
        if SplitMethod.SPLIT_METHOD_RANDOM == self.__configuration["test_configuration"]["method"]:
            df = df.sample(random_state=self.__configuration["test_configuration"]["random_state"], frac=1)
        else:
            df = df.iloc[:int(df.shape[0] * self.__configuration["test_configuration"]["split_ratio"])]

        self.__X = df.drop(self.target, axis=1)
        self.__y = df[self.target]

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

    def execute_task(self):
        """
        Execute the ML task
        NOTE: AutoGLUON automatically saves the model in a file
        Therefore we do not need to export it using pickle
        """
        if self.__configuration["task"] == 1:
            self.__classification()
        elif self.__configuration["task"] == 2:
            self.__regression()

    def __classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        self.__dataset_preparation()
        data = self.__X
        data[self.target] = self.__y
        model = TabularPredictor(label=self.target,
                                 problem_type="multiclass",
                                 path=self.__output_path).fit(
            data,
            time_limit=self.__configuration["runtime_constraints"]["runtime_limit"])

    def __regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        self.__dataset_preparation()
        data = self.__X
        data[self.target] = self.__y
        model = TabularPredictor(label=self.target,
                                 problem_type="regression",
                                 path=self.__output_path).fit(
            data,
            time_limit=self.__configuration["runtime_constraints"]["runtime_limit"])
