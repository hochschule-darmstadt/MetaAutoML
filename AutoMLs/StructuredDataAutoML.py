import os
import pandas as pd
import numpy as np
from AUTOCVE.AUTOCVE import AUTOCVEClassifier
from sklearn.metrics import f1_score
import pickle
from Utils.JsonUtil import get_config_property


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
        self.__time_limit = 60
        self.__configuration = configuration
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])
        target = self.__configuration["tabular_configuration"]["target"]["target"]
        self.__X = df.drop(target, axis=1)
        self.__y = df[target]

        return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        output_file = os.path.join(get_config_property('output-path'), "model_autocve.p")
        with open(output_file, "wb") as file:
            pickle.dump(model, file)

        return

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()

        auto_cls = AUTOCVEClassifier(
            max_evolution_time_secs=self.__time_limit,
            n_jobs=-1,
            verbose=1
        )
        auto_cls.optimize(self.__X, self.__y, subsample_data=1.0)
        best_voting_ensemble = auto_cls.get_best_voting_ensemble()
        best_voting_ensemble.fit(self.__X, self.__y)

        print("Best voting ensemble found:")
        print(best_voting_ensemble.estimators)
        print("Ensemble size: " + str(len(best_voting_ensemble.estimators)))
        print("Train Score: {}".format(best_voting_ensemble.score(self.__X, self.__y)))

        self.__export_model(best_voting_ensemble)

        return
