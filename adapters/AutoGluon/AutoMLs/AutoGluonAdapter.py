import os

from AdapterUtils import *
from AdapterTabularUtils import *
from autogluon.tabular import TabularPredictor
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
from autogluon.text import TextPredictor
from autogluon.vision import ImageDataset
from autogluon.multimodal import MultiModalPredictor
from AdapterUtils import prepare_tabular_dataset
from AutoGluonServer import data_loader
import shutil
import pandas as pd

class AutoGluonAdapter:
    """
    Implementation of the AutoML functionality for AutoGluon
    """
    def __init__(self, configuration: dict):
        """Init a new instance of AutoKerasAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30


        """
        self._configuration = configuration

        # set runtime limit from configuration, if it isn't specified its set to 30s
        if self._configuration["runtime_constraints"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["runtime_constraints"]["runtime_limit"]
        else:
            self._time_limit = 30

        # Interne spalten für Tabellen
        self._target = self._configuration["tabular_configuration"]["target"]["target"]


        # Maximum Itteration set to 3 if 0
        if self._configuration["runtime_constraints"]["max_iter"] == 0:
            self._max_iter = self._configuration["runtime_constraints"]["max_iter"] = 3

        # Erstelle den pfad der später verwendet wird.
        os.mkdir(os.path.join(get_config_property("output-path"), self._configuration["training_id"]))

        """

        self._result_path = os.path.join(self._configuration["result_folder_location"], "model_gluon.gluon")
        # this only sets the result path tbh.

    def start(self):
        """
        Execute the ML task
        NOTE: AutoGLUON automatically saves the model in a file
        Therefore we do not need to export it using pickle
        """
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":text_classification":
            self.__text_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()
        elif self._configuration["configuration"]["task"] == ":image_classification":
            self.__image_classification()
        elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
            self.__time_series_forecasting()

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        data = X
        data[y.name] = y
        classification_type = ""
        if len(y.unique()) == 2:
            classification_type = "binary"
        else:
            classification_type =  "multiclass"
        model = TabularPredictor(label=y.name,
                                 problem_type=classification_type,
                                 path=self._result_path).fit(
            data,
            time_limit=self._time_limit*60)
        #Fit methode already saves the model

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        data = X
        data[y.name] = y
        model = TabularPredictor(label=y.name,
                                 problem_type="regression",
                                 path=self._result_path).fit(
            data,
            time_limit=self._time_limit*60)
        #Fit methode already saves the model

    def __text_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        data = X
        data[y.name] = y
        classification_type = ""
        if len(y.unique()) == 2:
            classification_type = "binary"
        else:
            classification_type =  "multiclass"
        #Disable multi worker else training takes a while or doesnt complete
        #https://github.com/autogluon/autogluon/issues/2756
        hyperparameters = {"env.num_workers": 0}
        model = TextPredictor(label=y.name,
                                 problem_type=classification_type,
                                 path=self._result_path).fit(
            data,
            time_limit=self._time_limit*60, hyperparameters=hyperparameters)
        #Fit methode already saves the model

    def __image_classification(self):
        """"Execute image classification task and export the found model"""

        # Daten Laden
        #X_train, y_train, X_test, y_test = data_loader(self._configuration)

        # Einteilen
        data =  ImageDataset.from_folder(os.path.join(self._configuration['dataset_path'], 'train'))
        if len(data['label'].unique()) == 2:
            classification_type = "binary"
        else:
            classification_type =  "multiclass"
        #Disable multi worker else training takes a while or doesnt complete
        #https://github.com/autogluon/autogluon/issues/2756
        hyperparameters = {"env.num_workers": 0}
        model = MultiModalPredictor(label='label',problem_type=classification_type, path=self._result_path).fit(
            data,
            time_limit=self._time_limit*60, hyperparameters=hyperparameters)
        #Fit methode already saves the model

    def __time_series_forecasting(self):
        train, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(train, self._configuration)
        timestamp_column = ""
        #First get the datetime index column
        for column, dt in self._configuration["dataset_configuration"]["schema"].items():
            datatype = dt.get("datatype_selected", "")
            if datatype == "":
                datatype = dt["datatype_detected"]
            if dt.get("role_selected", "") == ":index" and datatype == ":datetime":
                timestamp_column = column
                break
        #Reset any index and imputation
        self._configuration = reset_index_role(self._configuration)
        X.reset_index(inplace = True)
        self._configuration = set_imputation_for_numerical_columns(self._configuration, X)
        train, test = data_loader(self._configuration)
        #reload dataset to load changed data
        X, y = prepare_tabular_dataset(train, self._configuration)
        data = X
        data[y.name] = y.values

        #Assign timeseries id
        data = data.assign(timeseries_id=1)

        ts_dataframe = TimeSeriesDataFrame.from_data_frame(data, id_column="timeseries_id", timestamp_column=timestamp_column)
        model = TimeSeriesPredictor(label=y.name,
                                eval_metric="sMAPE",
                                 path=self._result_path).fit(
            ts_dataframe,
            time_limit=self._time_limit*60)
        #Fit methode already saves the model

