import os
import warnings

import pandas as pd
import numpy as np
from AUTOCVE.AUTOCVE import AUTOCVEClassifier
from sklearn.metrics import f1_score
import pickle


class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration configuration of type dictionary
        """
        self.__time_limit = configuration["runtime_constraints"]["max_iter"]
        self.__configuration = configuration
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        self.__training_data_path = os.path \
            .join(self.__configuration["file_location"]
                  , self.__configuration["file_name"])
        df = pd.read_csv(self.__training_data_path)

        # __X is the entire data without the target column
        self.__X = df.drop(self.__configuration["tabular_configuration"]["target"]["target"], axis=1).to_numpy()
        # __y is only the target column
        self.__y = df[self.__configuration["tabular_configuration"]["target"]["target"]].to_numpy()
        # both __X and __y get converted to numpy arrays since AutoCVE cannot understand it otherwise

        return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open("templates/output/autocve-model.p", "wb") as file:
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

        try:
            auto_cls.optimize(self.__X, self.__y, subsample_data=1.0)
            best_voting_ensemble = auto_cls.get_best_voting_ensemble()
            best_voting_ensemble.fit(self.__X, self.__y)

            print("Best voting ensemble found:")
            print(best_voting_ensemble.estimators)
            print("Ensemble size: " + str(len(best_voting_ensemble.estimators)))
            print("Train Score: {}".format(best_voting_ensemble.score(self.__X, self.__y)))

            self.__export_model(best_voting_ensemble)

        except Exception as e:
            print(f"Critical error running autoCVE on {self.__configuration['file_name']}. The AutoCVE "
                  f"classifier encountered an exception during the optimisation process. This happens when the "
                  f"input dataset isn't in the correct format. AutoCVE can only process classification "
                  f"datasets with numerical values.")
            print(e)

        return
