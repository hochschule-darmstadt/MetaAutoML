import numpy as np
from AbstractAdapter import AbstractAdapter
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from tpot import TPOTClassifier
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split


class TPOTAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for TPOT
    """

    def __init__(self, configuration: dict):
        """Init a new instance of TPOTAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        super(TPOTAdapter, self).__init__(configuration)

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
        digits = load_digits()
        X_train, X_test, y_train, y_test = train_test_split(digits.data, digits.target,
                                                            train_size=0.75, test_size=0.25)
        pipeline_optimizer = TPOTClassifier(generations=5, population_size=20, cv=5,
                                            random_state=42, verbosity=2)
        pipeline_optimizer.fit(X_train, y_train)
        print(pipeline_optimizer.score(X_test, y_test))
        pipeline_optimizer.export('tpot_exported_pipeline.py')
        export_model(reg, self._configuration["result_folder_location"], 'model_TPOT.p')


    def __tabular_regression(self):
        pass
