from supervised.automl import AutoML
from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data, prepare_tabular_dataset, export_model

import shutil
from JsonUtil import get_config_property
import os

class MLJARAdapter(AbstractAdapter):
    """description of class"""

    def __init__(self, configuration):
        super(MLJARAdapter, self).__init__(configuration)
        #Create correct output folder for current session
        

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == 1:
                self.__tabular_classification()
            elif self._configuration["task"] == 2:
                self.__tabular_regression()

    def __tabular_classification(self):
        result_path = os.path.join(get_config_property("output-path"), self._configuration["session_id"], "Models")
        self.df = read_tabular_dataset_training_data(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        os.mkdir(result_path)
        automl = AutoML(total_time_limit=self._configuration["runtime_constraints"]["runtime_limit"], mode="Compete", results_path=result_path)
        automl.fit(X, y)

    def __tabular_regression(self):
        raise NotImplementedError()
