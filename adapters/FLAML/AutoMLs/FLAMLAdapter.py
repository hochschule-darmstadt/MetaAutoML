from flaml import AutoML

from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data, prepare_tabular_dataset, export_model

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

    def start(self):
        """
        Execute the ML task
        """
        if self._configuration["task"] == 1:
            self.__tabular_classification()
        elif self._configuration["task"] == 2:
            self.__tabular_regression()

    def __generate_settings(self):
        automl_settings = {"log_file_name": 'flaml.log'}
        if self._configuration["runtime_constraints"]["runtime_limit"] != 0:
            automl_settings.update({"time_budget": self._configuration["runtime_constraints"]["runtime_limit"]})
        if self._configuration["runtime_constraints"]["max_iter"] != 0:
            automl_settings.update({"max_iter": self._configuration["runtime_constraints"]["max_iter"]})
        return automl_settings

    def __tabular_classification(self):
        """
        Execute the classification task
        """
        self.df = read_tabular_dataset_training_data(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "metric": self._configuration["metric"] if self._configuration["metric"] != "" else 'accuracy',
            "task": 'classification',
        })

        automl.fit(X_train=X, y_train=y, **automl_settings)
        export_model(automl, 'model_flaml.p')

    def __tabular_regression(self):
        """
        Execute the regression task
        """
        self.df = read_tabular_dataset_training_data(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        automl = AutoML()
        automl_settings = self.__generate_settings()
        automl_settings.update({
            "metric": self._configuration["metric"] if self._configuration["metric"] != "" else 'rmse',
            "task": 'regression',
        })

        automl.fit(X_train=X, y_train=y, **automl_settings)
        export_model(automl, 'model_flaml.p')
