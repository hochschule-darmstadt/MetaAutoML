import os
from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property
# LightAutoML presets, task and report generation
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task

from predict_time_sources import feature_preparation


class LAMAAdapter:
    """Implementation of the AutoML functionality for GAMA

    Args:
        AbstractAdapter (_type_): _description_
    """

    def __init__(self, configuration: dict):
        """Init a new instance of EvalMLAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30

    def start(self):
        """Start the correct ML task functionality of GAMA"""
        print("strt auto ml req")
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__classification()

    def __classification(self):
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        task = Task('multiclass')
        N_THREADS = 4
        N_FOLDS = 5
        RANDOM_STATE = 42
        TEST_SIZE = 0.2
        TIMEOUT = 300
        TARGET_NAME = y.name
        X[TARGET_NAME] = y
        print(y)
        roles = {
            'target': TARGET_NAME,
            'drop': ['SK_ID_CURR']
        }
        automl = TabularAutoML(
            task = task,
            timeout = TIMEOUT,
            cpu_limit = N_THREADS,
            reader_params = {'n_jobs': N_THREADS, 'cv': N_FOLDS, 'random_state': RANDOM_STATE}
        )
        automl.fit_predict(X, roles = roles, verbose = 1)
        #export_model(pipeline_optimizer.fitted_pipeline_, self._configuration["result_folder_location"], 'model_LAMA.p')

        return

    def __regression(self):
        return



