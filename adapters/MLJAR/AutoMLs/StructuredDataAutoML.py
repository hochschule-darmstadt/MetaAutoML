import pickle
import os
import pandas as pd
from supervised.automl import AutoML
from Utils.JsonUtil import get_config_property
from AutoMLs.predict_time_sources import feature_preparation, DataType, SplitMethod


class StructuredDataAutoML(object):
    """description of class"""

    def __init__(self, configuration):
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
        output_file = os.path.join(get_config_property('output-path'), 'tmp', "mljar-model.p")
        with open(output_file, 'wb+') as f:
            pickle.dump(model, f)

    def classification(self):
        self.__read_training_data()
        self.__dataset_preparation()
        automl = AutoML(total_time_limit=self.__configuration["runtime_constraints"]["runtime_limit"], mode="Compete")
        automl.fit(self.__X, self.__y)
        self.__export_model(automl)

    def regression(self):
        raise NotImplementedError()
