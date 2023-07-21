
from AdapterUtils import *
from AdapterTabularUtils import *
from tpot import TPOTClassifier, TPOTRegressor
import TPOTParameterConfig as tpc
from TPOTWrapper import TPOTWrapper

class TPOTAdapter:
    """
    Implementation of the AutoML functionality for TPOT
    """

    def __init__(self, configuration: dict):
        """Init a new instance of TPOTAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration

    def start(self):
        """
        Start the correct ML task functionality of TPOT
        """
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__tabular_classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__tabular_regression()
            elif self._configuration["configuration"]["task"] == ":image_classification":
                self.__image_classification()

    def __tabular_classification(self):
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(":tpot", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), tpc.parameters)
        pipeline_optimizer = TPOTClassifier(**parameters,
                                            random_state=42, verbosity=2, max_time_mins=self._configuration["configuration"]["runtime_limit"])
        pipeline_optimizer.fit(X, y)
        export_model(pipeline_optimizer.fitted_pipeline_, self._configuration["result_folder_location"], 'model_TPOT.p')
        export_model(TPOTWrapper(pipeline_optimizer.fitted_pipeline_, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')


    def __tabular_regression(self):
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y, also_categorical=True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration, apply_feature_extration=True)
        parameters = translate_parameters(":tpot", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), tpc.parameters)

        pipeline_optimizer = TPOTRegressor(**parameters,
                                            random_state=42, verbosity=2, max_time_mins=self._configuration["configuration"]["runtime_limit"])
        pipeline_optimizer.fit(X, y)
        export_model(pipeline_optimizer.fitted_pipeline_, self._configuration["result_folder_location"], 'model_TPOT.p')
        export_model(TPOTWrapper(pipeline_optimizer.fitted_pipeline_, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    def __image_classification(self):
        X, y = data_loader(self._configuration, perform_splitting=False, as_2darray=True)

        parameters = translate_parameters(":tpot", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), tpc.parameters)
        pipeline_optimizer = TPOTClassifier(**parameters,
                                            random_state=42, verbosity=2, max_time_mins=self._configuration["configuration"]["runtime_limit"])
        pipeline_optimizer.fit(X, y)
        export_model(pipeline_optimizer.fitted_pipeline_, self._configuration["result_folder_location"], 'model_TPOT.p')

