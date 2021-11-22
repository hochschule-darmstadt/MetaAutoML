import os
import pandas as pd
from AUTOCVE.AUTOCVE import AUTOCVEClassifier
from sklearn.metrics import f1_score
import pickle
from Utils.JsonUtil import get_config_property


class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, json: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        self.__time_limit = 30
        self.__json = json
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        self.__training_data_path = os.path \
            .join(self.__json["file_location"]
                  , self.__json["file_name"])
        df = pd.read_csv(self.__training_data_path)

        # convert all object columns to categories, because autosklearn only supports numerical, bool and categorical features
        df[df.columns] = df[df.columns].apply(lambda col:pd.Categorical(col).codes)

        # __X is the entire data without the target column
        self.__X = df.drop(self.__json["configuration"]["target"], axis=1).to_numpy()
        # __y is only the target column
        self.__y = df[self.__json["configuration"]["target"]].to_numpy()
        # both __X and __y get converted to numpy arrays since AutoCVE cannot understand it otherwise

        return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        with open("templates/output/autosklearn-model.p", "wb") as file:
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
        best_voting_ensemble = autocve.get_best_voting_ensemble()
        best_voting_ensemble.fit(self.__X, self.__y)

        self.__export_model(auto_cls)

        return
