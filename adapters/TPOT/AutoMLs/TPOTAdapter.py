import numpy as np
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from tpot import TPOTClassifier
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split


class TPOTAdapter:
    """
    Implementation of the AutoML functionality for TPOT
    """

    def __init__(self, configuration: dict):
        """Init a new instance of TPOTAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration

    def start(self):
        """
        Start the correct ML task functionality of TPOT
        """
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__tabular_classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__tabular_regression()

    def __tabular_classification(self):
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        pipeline_optimizer = TPOTClassifier(generations=5, population_size=20, cv=5,
                                            random_state=42, verbosity=2, max_time_mins=self._configuration["configuration"]["runtime_limit"]*60)
        pipeline_optimizer.fit(X, y)
        export_model(pipeline_optimizer, self._configuration["result_folder_location"], 'model_TPOT.p')


    def __tabular_regression(self):
        pass
