import autokeras as ak
import numpy as np
from AbstractAdapter import AbstractAdapter
from AdapterUtils import data_loader, export_model, prepare_tabular_dataset


class AutoKerasAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for AutoKeras
    """
    def __init__(self, configuration: dict):
        """Init a new instance of AutoKerasAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        super(AutoKerasAdapter, self).__init__(configuration)

    def start(self):
        """Start the correct ML task functionality of AutoKeras"""
        if True:
            if self._configuration["configuration"]["task"] == ":tabular_classification":
                self.__tabular_classification()
            elif self._configuration["configuration"]["task"] == ":tabular_regression":
                self.__tabular_regression()
            elif self._configuration["configuration"]["task"] == ":image_classification":
                self.__image_classification()
            elif self._configuration["configuration"]["task"] == ":image_regression":
                self.__image_regression()
            elif self._configuration["configuration"]["task"] == ":text_classification":
                self.__text_classification()
            elif self._configuration["configuration"]["task"] == ":text_regression":
                self.__text_regression()
            elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
                self.__time_series_forecasting()

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        clf = ak.StructuredDataClassifier(overwrite=True,
                                          max_trials=3,
                                          # metric=self._configuration['metric'],
                                          directory=self._configuration["model_folder_location"],
                                          seed=42)
                                          
        clf.fit(x=X, y=y)
        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        reg = ak.StructuredDataRegressor(overwrite=True,
                                          max_trials=3,
                                         # metric=self._configuration['metric'],
                                         directory=self._configuration["model_folder_location"],
                                         seed=42)
        
        reg.fit(x=X, y=y)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_classification(self):
        """"Execute image classification task and export the found model"""

        X_train, y_train, X_test, y_test = data_loader(self._configuration)

        clf = ak.ImageClassifier(overwrite=True, 
                                          max_trials=3,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        #clf.fit(train_data, epochs=self._configuration["runtime_constraints"]["epochs"])
        clf.fit(x = X_train, y = y_train, epochs=1)

        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_regression(self):
        """Execute image regression task and export the found model"""

        X_train, y_train, X_val, y_val = data_loader(self._configuration)

        reg = ak.ImageRegressor(overwrite=True, 
                                          max_trials=3,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])
                                
        reg.fit(x = X_train, y = y_train)

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __text_classification(self):
        """Execute text classifiction task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        reg = ak.TextClassifier(overwrite=True, 
                                # NOTE: bert models will fail with out of memory errors
                                #   even with 32GB GB RAM
                                # the first model is a non-bert transformer  
                                max_trials=1,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])
                                
        reg.fit(x = np.array(X), y = np.array(y), epochs=1)

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __text_regression(self):
        """Execute text regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        reg = ak.TextClassifier(overwrite=True, 
                                          max_trials=3,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])
                                
        reg.fit(x = np.array(X), y = np.array(y))

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __time_series_forecasting(self):
        """Execute time series forecasting task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        reg = ak.TimeseriesForecaster(overwrite=True, 
                                          max_trials=3,
                                # metric=self._configuration['metric'],
                                seed=42,
                                directory=self._configuration["model_folder_location"])
                                
        reg.fit(x = np.array(X), y = np.array(y))

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')
