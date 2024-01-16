import numpy as np
from AdapterUtils import *
from AdapterTabularUtils import *
import pandas as pd
import json
import os
from JsonUtil import get_config_property
from H2OWrapper import H2OWrapper
import H2OParameterConfig as h2opc
import h2o
from h2o.automl import H2OAutoML


# # Laden Sie Ihre Daten in ein H2O Frame
# df = h2o.import_file("your_data.csv")

# # F�r eine Klassifikation: Stellen Sie sicher, dass Ihre Zielvariable als Faktor (also als kategorisch) gesetzt ist, bevor Sie mit dem Training beginnen. Dies k�nnen Sie mit der asfactor() Methode tun:
# target = 'your_target_column'
# df[target] = df[target].asfactor()  # Konvertiert die Zielvariable in einen Faktor, wenn es sich um eine Klassifikation handelt

# # F�r eine Regression: Stellen Sie sicher, dass Ihre Zielvariable als numerisch gesetzt ist.
# target = 'your_target_column'
# df[target] = df[target].asnumeric() # Konvertiert die Zielvariable in Numeric, wenn es sich um eine Regression handelt

# # Konvertieren Sie das Pandas DataFrame in ein H2O Frame
# h2o_df = h2o.H2OFrame(df)


class H2OAdapter:
    """
    Implementation of the AutoML functionality for H2O
    """
    def __init__(self, configuration: dict):
        """Init a new instance of H2OAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        h2o.init()
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"] * 60
        else:
            self._time_limit = 30

    def start(self):
        """Start the correct ML task functionality of H2O"""
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            print("test1")
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()


    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""

        self.df, test = data_loader(self._configuration)
        features, targets = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)

        #df[target].asfactor()
        parameters = translate_parameters(":h2o_automl", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), h2opc.parameters)

        # remove XGBoost if its not in the Selected ML Libaries
        if not(':xgboost_lib' in self._configuration["configuration"].get('selected_ml_libraries', {})) and 'include_algos' in parameters and ('XGBoost' in parameters['include_algos']):
            parameters['include_algos'].remove('XGBoost')

        pandasJoineddf = pd.concat([features, targets], axis=1)

        aml = H2OAutoML(max_runtime_secs = self._time_limit, seed = 1, **parameters)
        aml.train(y = targets.name, training_frame = h2o.H2OFrame(pandasJoineddf))
        # The leader model is stored here
        # View the AutoML Leaderboard
        leaderboard = aml.leaderboard
        best_model = aml.get_best_model()
        #export
        model_path = h2o.save_model(model=best_model, path=self._configuration["result_folder_location"])
        os.rename(model_path, os.path.join(self._configuration["result_folder_location"], 'model_h2o.p'))
        #export_model(best_model, self._configuration["result_folder_location"], 'model_h2o.p')
        H2OWrapper(best_model, self._configuration)
        export_model(H2OWrapper(best_model, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        features, targets = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        df[target].asfactor()
        parameters = translate_parameters(":h2o", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), h2opc.parameters)
        parameters.update({"max_trials": self._configuration["configuration"]["runtime_limit"]})
        aml = H2OAutoML(max_runtime_secs = 35, seed = 1)
        aml.train(y = h2o.H2OFrame(targets), training_frame = h2o.H2OFrame(features))
        # The leader model is stored here
        # View the AutoML Leaderboard
        lb = aml.leaderboard
        lb.head(rows=lb.nrows)  # Print all rows instead of default (10 rows)


    # def __tabular_classification(self):
    #     """Execute the tabular classification task and export the found model"""

    #     self.df, test = data_loader(self._configuration)
        # X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        # parameters = translate_parameters(":h2o", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
        # parameters.update({"max_trials": self._configuration["configuration"]["runtime_limit"]})
    #     clf = ak.StructuredDataClassifier(overwrite=True,
    #                                       **parameters,
    #                                       directory=self._configuration["model_folder_location"],
    #                                       seed=42)
    #     H2OAutoML.train()
    #     clf.fit(x=X, y=y, epochs=1, verbose=2)
    #     export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')
    #     export_model(H2OWrapper(clf, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    # def __tabular_regression(self):
    #     """Execute the tabular regression task and export the found model"""

    #     self.df, test = data_loader(self._configuration)
    #     X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
    #     parameters = translate_parameters(":h2o", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), akpc.parameters)
    #     parameters.update({"max_trials": self._configuration["configuration"]["runtime_limit"]})
    #     reg = ak.StructuredDataRegressor(overwrite=True,
    #                                       **parameters,
    #                                      directory=self._configuration["model_folder_location"],
    #                                      seed=42)

    #     reg.fit(x=X, y=y, epochs=1, verbose=2)
    #     export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')
    #     export_model(H2OWrapper(reg, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')
