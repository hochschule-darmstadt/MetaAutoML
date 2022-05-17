import os
import pandas as pd
import numpy as np
from AUTOCVE.AUTOCVE import AUTOCVEClassifier
import pickle
from JsonUtil import get_config_property
from predict_time_sources import feature_preparation, DataType, SplitMethod
from AbstractTabularDataAutoML import AbstractTabularDataAutoML


class TabularDataAutoML(AbstractTabularDataAutoML):
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
        super().__init__(configuration)

    def _cast_target(self):
        target_dt = self._configuration["tabular_configuration"]["target"]["type"]
        if DataType(target_dt) is DataType.DATATYPE_INT or \
                DataType(target_dt) is DataType.DATATYPE_CATEGORY or \
                DataType(target_dt) is DataType.DATATYPE_BOOLEAN:
            self._y = self._y.astype('int')
        elif DataType(target_dt) is DataType.DATATYPE_FLOAT:
            self._y = self._y.astype('float')

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        output_file = os.path.join(get_config_property(
            'output-path'), 'tmp', "autocve-model.p")
        with open(output_file, "wb+") as file:
            pickle.dump(model, file)

    def __classification(self):
        """
        Execute the classification task
        """
        self._read_training_data()
        self._dataset_preparation()
        self._convert_data_to_numpy()

        auto_cls = AUTOCVEClassifier(
            max_evolution_time_secs=self._time_limit,
            n_jobs=-1,
            verbose=1
        )

        try:
            auto_cls.optimize(self._X, self._y, subsample_data=1.0)
            best_voting_ensemble = auto_cls.get_best_voting_ensemble()
            best_voting_ensemble.fit(self._X, self._y)

            print("Best voting ensemble found:")
            print(best_voting_ensemble.estimators)
            print("Ensemble size: " + str(len(best_voting_ensemble.estimators)))
            print("Train Score: {}".format(
                best_voting_ensemble.score(self._X, self._y)))

            self.__export_model(best_voting_ensemble)

        except Exception as e:
            print(f"Critical error running autoCVE on {self._configuration['file_name']}. The AutoCVE "
                  f"classifier encountered an exception during the optimisation process. This might have happened "
                  f"because input dataset isn't in the correct format. AutoCVE can only process classification "
                  f"datasets with numerical values.")
            print(e)

    def execute_task(self):
        """
        Execute the ML task
        """
        if self._configuration["task"] == 1:
            self.__classification()
        else:
            raise ValueError(
                f'{get_config_property("adapter-name")} was called with an invalid task: task=={self._configuration["task"]}. The only valid task is task==1'
            )
