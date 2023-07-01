import os
from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property
# LightAutoML presets, task and report generation
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task

from predict_time_sources import feature_preparation
import LAMAConfigParameter as lpc

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
            self._time_limit = 300

    """
    !warning: currently there is a problem, that when metric and loss function in classification are not entropy, it will raise an error
    that no model is found
    """
    def start(self):
        """Start the correct ML task functionality of GAMA"""
        print("strt auto ml req")
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__regression()

    def __classification(self):
        """ clasifier
        """
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), lpc.task_config)
        task = Task(name='multiclass', metric=parameters['metric'], loss=parameters['loss'])
        # task = Task(name='multiclass',**parameters)
        RANDOM_STATE = 42
        TIMEOUT = self._time_limit
        TARGET_NAME = y.name
        X[TARGET_NAME] = y
        roles = {
            'target': TARGET_NAME,
        }
        automl = TabularAutoML(
            task = task,
            timeout = TIMEOUT,
            reader_params = {'random_state': RANDOM_STATE}
        )
        automl.fit_predict(X, roles = roles, verbose = 1)
        export_model(automl, self._configuration["result_folder_location"], 'model_LAMA.p')

        return

    def __regression(self):
        """ regression
        """
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        parameters = translate_parameters(self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), lpc.task_config)
        task = Task(name='reg',**parameters)
        RANDOM_STATE = 42
        TIMEOUT = self._time_limit
        TARGET_NAME = y.name
        X[TARGET_NAME] = y
        roles = {
            'target': TARGET_NAME,
        }
        automl = TabularAutoML(
            task = task,
            timeout = TIMEOUT,
            reader_params = {'random_state': RANDOM_STATE}
        )
        automl.fit_predict(X, roles = roles, verbose = 1)
        export_model(automl, self._configuration["result_folder_location"], 'model_LAMA.p')

        return



