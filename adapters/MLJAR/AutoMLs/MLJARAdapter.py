from supervised.automl import AutoML
from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data, prepare_tabular_dataset, export_model



class MLJARAdapter(AbstractAdapter):
    """description of class"""

    def __init__(self, configuration):
        super(MLJARAdapter, self).__init__(configuration)
        

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == 1:
                self.__tabular_classification()
            elif self._configuration["task"] == 2:
                self.__tabular_regression()

    def __tabular_classification(self):
        self.df = read_tabular_dataset_training_data(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        automl = AutoML(total_time_limit=self._configuration["runtime_constraints"]["runtime_limit"], mode="Compete")
        automl.fit(X, y)
        #TODO: Correct reimport, MLJAR automatically save every model
        #export_model(automl, "mljar-model.p")

    def __tabular_regression(self):
        raise NotImplementedError()
