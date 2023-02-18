
from AdapterUtils import *
from AdapterTabularUtils import *
from tpot import TPOTClassifier, TPOTRegressor


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

    def __tabular_classification(self):
        train, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration, reload = set_encoding_for_string_columns(self._configuration, X, also_categorical=True)
        if reload:
            train, test = data_loader(self._configuration)
            #reload dataset to load changed data
            X, y = prepare_tabular_dataset(train, self._configuration)

        pipeline_optimizer = TPOTClassifier(generations=5, population_size=20, cv=5,
                                            random_state=42, verbosity=2, max_time_mins=self._configuration["configuration"]["runtime_limit"]*60)
        pipeline_optimizer.fit(X, y)
        export_model(pipeline_optimizer.fitted_pipeline_, self._configuration["result_folder_location"], 'model_TPOT.p')


    def __tabular_regression(self):
        train, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(train, self._configuration)
        #Apply encoding to string
        self._configuration, reload = set_encoding_for_string_columns(self._configuration, X, also_categorical=True)
        if reload:
            train, test = data_loader(self._configuration)
            #reload dataset to load changed data
            X, y = prepare_tabular_dataset(train, self._configuration)

        pipeline_optimizer = TPOTRegressor(verbosity=2, max_time_mins=self._configuration["configuration"]["runtime_limit"]*60)
        pipeline_optimizer.fit(X, y)
        export_model(pipeline_optimizer, self._configuration["result_folder_location"], 'model_TPOT.p')
