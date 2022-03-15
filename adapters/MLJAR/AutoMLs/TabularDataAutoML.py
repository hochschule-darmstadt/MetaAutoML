import pickle
import os
import pandas as pd
from supervised.automl import AutoML
from JsonUtil import get_config_property
from predict_time_sources import feature_preparation, DataType, SplitMethod
from AbstractTabularDataAutoML import AbstractTabularDataAutoML


class TabularDataAutoML(AbstractTabularDataAutoML):
    """description of class"""

    def __init__(self, configuration):
        super().__init__(configuration)
        
    def __export_model(self, model):
        output_file = os.path.join(get_config_property('output-path'), 'tmp', "mljar-model.p")
        with open(output_file, 'wb+') as f:
            pickle.dump(model, f)

    def classification(self):
        self._read_training_data()
        self._dataset_preparation()
        automl = AutoML(total_time_limit=self._configuration["runtime_constraints"]["runtime_limit"], mode="Compete")
        automl.fit(self._X, self._y)
        self.__export_model(automl)

    def regression(self):
        raise NotImplementedError()
