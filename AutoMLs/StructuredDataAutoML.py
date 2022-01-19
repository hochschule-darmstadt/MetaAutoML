import os
import pandas as pd
import numpy as np
from AUTOCVE.AUTOCVE import AUTOCVEClassifier
import pickle
from Utils.JsonUtil import get_config_property
from predict_time_sources import feature_preparation, DataType, SplitMethod
    
    
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
        # set runtime limit from configuration, if it isn't specified its set to 30s
        if configuration["runtime_constraints"]["runtime_limit"] > 0:
            self.__time_limit = configuration["runtime_constraints"]["runtime_limit"]
        else:
            self.__time_limit = 30
        self.__configuration = configuration

    def __read_training_data(self):
        """
        Read the training dataset from disk
        """
        df = pd.read_csv(os.path.join(self.__configuration["file_location"], self.__configuration["file_name"]),
                         **self.__configuration["file_configuration"])

        # split training set
        if SplitMethod.SPLIT_METHOD_RANDOM == self.__configuration["test_configuration"]["method"]:
            df = df.sample(random_state=self.__configuration["test_configuration"]["random_state"], frac=1)
        else:
            df = df.iloc[:int(df.shape[0] * self.__configuration["test_configuration"]["split_ratio"])]

        target = self.__configuration["tabular_configuration"]["target"]["target"]
        self.__X = df.drop(target, axis=1)
        self.__y = df[target]

    def __dataset_preparation(self):
        feature_preparation(self.__X, self.__configuration["tabular_configuration"]["features"].items())
        self.__cast_target()

    def __cast_target(self):
        target_dt = self.__configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_INT or \
                DataType(target_dt) is DataType.DATATYPE_CATEGORY or \
                DataType(target_dt) is DataType.DATATYPE_BOOLEAN:
            self.__y = self.__y.astype('int')
        elif DataType(target_dt) is DataType.DATATYPE_FLOAT:
            self.__y = self.__y.astype('float')

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        output_file = os.path.join(get_config_property('output-path'), 'tmp', "autocve-model.p")
        with open(output_file, "wb") as file:
            pickle.dump(model, file)

    def __convert_data_to_numpy(self):
        self.__X = self.__X.to_numpy()
        self.__X = np.nan_to_num(self.__X, 0)
        self.__y = self.__y.to_numpy()

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        self.__dataset_preparation()
        self.__convert_data_to_numpy()

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
                  f"classifier encountered an exception during the optimisation process. This might have happened "
                  f"because input dataset isn't in the correct format. AutoCVE can only process classification "
                  f"datasets with numerical values.")
            print(e)

    def execute_task(self):
        """
        Execute the ML task
        """
        if self.__configuration["task"] == 1:
            self.classification()
        else:
            raise ValueError(
                f'{get_config_property("adapter-name")} was called with an invalid task: task=={self.__configuration["task"]}. The only valid task is task==1')
