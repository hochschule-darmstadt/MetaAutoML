import os

from AbstractAdapter import AbstractAdapter
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from flaml import AutoML
from JsonUtil import get_config_property


class FLAMLAdapter(AbstractAdapter):
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
        super(FLAMLAdapter, self).__init__(configuration)
        self._result_path = configuration["model_folder_location"]
        self._log_file_path = os.path.join(self._result_path, "flaml.log")

    def start(self):
        """
        Execute the ML task
        """
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()

    def __generate_settings(self):
        automl_settings = {"log_file_name": 'flaml.log'}
        if self._configuration["configuration"]["runtime_limit"] != 0:
            automl_settings.update({"time_budget": self._configuration["configuration"]["runtime_limit"]})
        return automl_settings

    def __tabular_classification(self):
        """
        Execute the classification task
        """
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            #"metric": self._configuration["configuration"]["metric"] if self._configuration["configuration"]["metric"] != "" else 'accuracy',
            "metric": 'accuracy',
            "task": 'classification',
            "log_file_name": self._log_file_path,
        })

        automl.fit(X_train=X, y_train=y, **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')

    def __tabular_regression(self):
        """
        Execute the regression task
        """
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            #"metric": self._configuration["configuration"]["metric"] if self._configuration["configuration"]["metric"] != "" else 'accuracy',
            "metric": 'accuracy',
            "task": 'regression',
            "log_file_name": self._log_file_path,
        })

        automl.fit(X_train=X, y_train=y, **automl_settings)
        export_model(automl, self._configuration["result_folder_location"], 'model_flaml.p')
