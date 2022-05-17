from predict_time_sources import feature_preparation, DataType, SplitMethod

import pandas as pd
import os
import numpy as np

class AbstractTabularDataAutoML:
    def __init__(self, configuration: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        # set runtime limit from configuration, if it isn't specified its set to 30s
        self._configuration = configuration
        if self._configuration["runtime_constraints"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["runtime_constraints"]["runtime_limit"]
        else:
            self._time_limit = 30
        self._target = self._configuration["tabular_configuration"]["target"]["target"]
        if self._configuration["runtime_constraints"]["max_iter"] == 0:
            self._max_iter = self._configuration["runtime_constraints"]["max_iter"] = 3
        
    def _cast_target(self):
        target_dt = self._configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_CATEGORY:
            self._y = self._y.astype('category')
        elif DataType(target_dt) is DataType.DATATYPE_BOOLEAN:
            self._y = self._y.astype('bool')
        elif DataType(target_dt) is DataType.DATATYPE_INT:
            self._y = self._y.astype('int')
        elif DataType(target_dt) is DataType.DATATYPE_FLOAT:
            self._y = self._y.astype('float')
    
    def _read_training_data(self):
        """
        Read the training dataset from disk
        """
        df = pd.read_csv(os.path.join(self._configuration["file_location"], self._configuration["file_name"]),
                         **self._configuration["file_configuration"])

        print(self._configuration)

        # split training set
        if SplitMethod.SPLIT_METHOD_RANDOM == self._configuration["test_configuration"]["method"]:
            df = df.sample(random_state=self._configuration["test_configuration"]["random_state"], frac=1)
        else:
            df = df.iloc[:int(df.shape[0] * self._configuration["test_configuration"]["split_ratio"])]

        self._X = df.drop(self._target, axis=1)
        self._y = df[self._target]
        
    def _dataset_preparation(self):
        feature_preparation(self._X, self._configuration["tabular_configuration"]["features"].items())
        self._cast_target()
        
    def _convert_data_to_numpy(self):
        self._X = self._X.to_numpy()
        self._X = np.nan_to_num(self._X, 0)
        self._y = self._y.to_numpy()