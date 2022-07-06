import os

from AbstractAdapter import AbstractAdapter
from AdapterUtils import (convert_X_and_y_dataframe_to_numpy, export_model,
                          prepare_tabular_dataset, data_loader)
from AUTOCVE.AUTOCVE import AUTOCVEClassifier
from JsonUtil import get_config_property


class AutoCVEAdapter(AbstractAdapter):
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
        self._result_path = os.path.join(get_config_property("output-path"), self._configuration["session_id"])

    def __tabular_classification(self):
        """
        Execute the classification task
        """
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X, y = convert_X_and_y_dataframe_to_numpy(X, y)

        auto_cls = AUTOCVEClassifier(
            max_evolution_time_secs=self._time_limit,
            n_jobs=-1,
            verbose=1
        )

        try:
            auto_cls.optimize(X, y, subsample_data=1.0)
            best_voting_ensemble = auto_cls.get_best_voting_ensemble()
            best_voting_ensemble.fit(X, y)

            print("Best voting ensemble found:")
            print(best_voting_ensemble.estimators)
            print("Ensemble size: " + str(len(best_voting_ensemble.estimators)))
            print("Train Score: {}".format(best_voting_ensemble.score(X, y)))

            export_model(best_voting_ensemble, self._configuration["session_id"], "autocve-model.p")

        except Exception as e:
            print(f"Critical error running autoCVE on {self._configuration['file_name']}. The AutoCVE "
                  f"classifier encountered an exception during the optimisation process. This might have happened "
                  f"because input dataset isn't in the correct format. AutoCVE can only process classification "
                  f"datasets with numerical values.")
            print(e)

    def start(self):
        """
        Execute the ML task
        """
        if self._configuration["task"] == ":tabular_classification":
            self.__tabular_classification()
        else:
            raise ValueError(
                f'{get_config_property("adapter-name")} was called with an invalid task: task=={self._configuration["task"]}. The only valid task is task==1')
