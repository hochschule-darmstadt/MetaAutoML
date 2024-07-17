import os
from AdapterUtils import *
from AdapterTabularUtils import *
# LightAutoML presets, task and report generation
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task

from predict_time_sources import feature_preparation
import LAMAConfigParameter as lpc
from LAMAWrapper import LAMAWrapper

class LAMAAdapter:
    """Implementation of the AutoML functionality for LAMA

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
        """Start the correct ML task functionality of LAMA"""
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
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(":lama", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), lpc.parameters)
        if len(y.unique()) == 2 and  set(y.unique()) == {0, 1}: #LAMA can only predict 0 and 1 in binary cases, when target is anything else the values wont match later
            #task = Task(name='binary', metric=parameters['metric'], loss=parameters['loss'])
            task = Task(name='binary', **parameters)
        else:
            #task = Task(name='multiclass', metric=parameters['metric'], loss=parameters['loss'])
            task = Task(name='multiclass', **parameters)
        # task = Task(name='multiclass',**parameters)
        RANDOM_STATE = 42
        TARGET_NAME = y.name
        #X[TARGET_NAME] = y
        X = pd.concat([X, y], axis=1)
        roles = {
            'target': TARGET_NAME,
        }
        automl = TabularAutoML(
            task = task,
            timeout = self._configuration["configuration"]["runtime_limit"] * 60,
            reader_params = {'random_state': RANDOM_STATE}
        )
        automl.fit_predict(X, roles = roles, verbose = 1)
        export_model(automl, self._configuration["result_folder_location"], 'model_LAMA.p')
        export_model(LAMAWrapper(automl, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

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
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(":lama", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), lpc.parameters)
        task = Task(name='reg',**parameters)
        RANDOM_STATE = 42
        TARGET_NAME = y.name
        X[TARGET_NAME] = y
        roles = {
            'target': TARGET_NAME,
        }
        automl = TabularAutoML(
            task = task,
            timeout = self._configuration["configuration"]["runtime_limit"] * 60,
            reader_params = {'random_state': RANDOM_STATE}
        )
        automl.fit_predict(X, roles = roles, verbose = 1)
        export_model(automl, self._configuration["result_folder_location"], 'model_LAMA.p')
        export_model(LAMAWrapper(automl, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

        return



