import os

from AbstractAdapter import AbstractAdapter
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from autogluon.tabular import TabularDataset, TabularPredictor, TextPredictor
from JsonUtil import get_config_property#
from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data, prepare_tabular_dataset, export_model
from AutoGluonServer import data_loader
import shutil

from autogluon.vision import ImagePredictor, ImageDataset

class AutoGluonAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for AutoGluon
    """
    def __init__(self, configuration: dict):
        """Init a new instance of AutoKerasAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        super().__init__(configuration)


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
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()
        elif self._configuration["configuration"]["task"] == ":image_classification":
            self.__image_classification()
        elif self._configuration["configuration"]["task"] == ":text_classification":
            self.__text_classification
        elif self._configuration["configuration"]["task"] == ":text_regression":
            self.__text_regression

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        data = X
        data[self._target] = y
        model = TabularPredictor(label=self._target,
                                 problem_type="multiclass",
                                 path=self._result_path).fit(
            data,
            time_limit=self._time_limit)
        #Fit methode already saves the model

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        data = X
        data[self._target] = y
        model = TabularPredictor(label=self._target,
                                 problem_type="regression",
                                 path=self._result_path).fit(
            data,
            time_limit=self._time_limit)
        #Fit methode already saves the model

    def __image_classification(self):
        """"Execute image classification task and export the found model"""

        # Daten Laden 
        train , test = data_loader(self._configuration)
        
        # Einteilen 
        set_hyperparameters={ 
            'batch_size': self._configuration["test_configuration"]["batch_size"], 
            'epochs': self._configuration["runtime_constraints"]["epochs"] 
            }
        
        model = ImagePredictor(
            label=self._target,
            path=self._result_path)
        
         # Trainieren 
        model.fit(
            train , 
            #hyperparameters=set_hyperparameters , 
            time_limit=self._time_limit  ) 

    def __text_classification(self):
        """Execute the text classification task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        data = X
        data[self._target] = y
        model = TextPredictor(label=self._target,
                                 problem_type="multiclass",
                                 path=self._result_path).fit(
            data,
            time_limit=self._time_limit)
        #Fit methode already saves the model

    def __text_regression(self):
        """Execute the text regression task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        data = X
        data[self._target] = y
        model = TextPredictor(label=self._target,
                                 problem_type="regression",
                                 path=self._result_path).fit(
            data,
            time_limit=self._time_limit)
        #Fit methode already saves the model
