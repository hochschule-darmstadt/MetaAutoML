import os

from AdapterUtils import *
from AdapterTabularUtils import *
from JsonUtil import get_config_property


from predict_time_sources import feature_preparation
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from gama import GamaClassifier,GamaRegressor
from gama.search_methods import AsynchronousSuccessiveHalving, AsyncEA, RandomSearch
import GAMAParameterConfig as gpc
from GAMAWrapper import GAMAWrapper

class GAMAAdapter:
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
                self.__regression()

    def __classification(self):
        """Execute the tabular classification task and export the found model"""
        self.df, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y)

        self.df, test = data_loader(self._configuration)
        X, y, = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        out_dir = (self._configuration["result_folder_location"] + "\\gama\\")
        parameters = translate_parameters(":gama", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), gpc.parameters)
        automl = GamaClassifier(max_total_time=self._time_limit*60, store="nothing", n_jobs=1, **parameters,output_directory=out_dir ,search=self.__get_search_method())
        automl.fit(X, y)

        export_model(automl, self._configuration["result_folder_location"], 'GAMA.p')
        export_model(GAMAWrapper(automl, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')
        return

    def __regression(self):
        """Execute the tabular regression task and export the found model"""
        self.df, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        self._configuration = set_encoding_for_string_columns(self._configuration, X, y)

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)

        parameters = translate_parameters(":gama", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), gpc.parameters)
        out_dir = (self._configuration["result_folder_location"] + "\\gama\\")
        automl = GamaRegressor(max_total_time=self._time_limit*60, store="nothing", n_jobs=1, **parameters,output_directory=out_dir, search=self.__get_search_method())
        automl.fit(X, y)

        export_model(automl, self._configuration["result_folder_location"], 'GAMA.p')
        export_model(GAMAWrapper(automl, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')


        return

    def __get_search_method(self):
        """get tuner class or search method in gama
        return none when not setted
        Returns:
            tuner class object: tuner obj
        """
        tuner_dict = {
            ':random' : RandomSearch() ,
            ':async_ea' : AsyncEA() ,
            ':async_successive_halving' : AsynchronousSuccessiveHalving() ,
        }
        try:
            return tuner_dict[self._configuration['configuration']['parameters'][':tuner_class_gama']['values'][0]]
        except:
            print("no tuner param")

        return AsyncEA() #default


