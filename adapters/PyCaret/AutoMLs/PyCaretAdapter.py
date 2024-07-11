import os

from AdapterUtils import *
from AdapterTabularUtils import *
import numpy as np
from sklearn.impute import SimpleImputer
import pandas as pd
import json
import PyCaretParameterConfig as ppc
from PycaretWrapper import PycaretWrapper
from pycaret.clustering import *
import subprocess # to start Dashboard

class PyCaretAdapter:
    """
    Implementation of the AutoML functionality for PyCaret
    """

    def __init__(self, configuration: dict):
        """Init a new instance of PyCaretAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30
        self._result_path = configuration["model_folder_location"]
        self._log_file_path = os.path.join(self._result_path, "PyCaret.log")

    def start(self):
        """Start the correct ML task functionality of PyCaret"""
        if self._configuration["configuration"]["task"] == ":tabular_classification":
            self.__tabular_classification()
        elif self._configuration["configuration"]["task"] == ":tabular_regression":
            self.__tabular_regression()
        elif self._configuration["configuration"]["task"] == ":time_series_forecasting":
            self.__time_series_forecasting()
        elif self._configuration["configuration"]["task"] == ":tabular_clustering":
            self.__tabular_clustering()

    def __tabular_classification(self):
        """Execute the tabular classification task and export the found model"""
        from pycaret.classification import setup, compare_models, save_model, create_model, finalize_model, tune_model

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        X[y.name] = y
        #TODO If index is set, index is somehow removed within pycaret and added as empty dataframe which crashes
        #Issue https://github.com/pycaret/pycaret/issues/3324

        parameters = translate_parameters(":pycaret", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), ppc.parameters)
        automl = setup(data = X, target = y.name)
        best = compare_models(budget_time=self._configuration["configuration"]["runtime_limit"] / 3) #Setup for max 1/3 of time
        model = create_model(best)
        tuned = tune_model(model, **parameters)
        fn_model = finalize_model(tuned)
        save_model(fn_model, os.path.join(self._configuration["result_folder_location"], 'model_pycaret'))
        export_model(PycaretWrapper(fn_model, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

        #export_model(automl, self._configuration["result_folder_location"], 'model_pycaret.p')

    def __tabular_clustering(self):
        """Execute the tabular clustering task and export the found model"""
        self.df, test = data_loader(self._configuration, perform_splitting=False)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)

        parameters = translate_parameters(":pycaret", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), ppc.parameters)

        save_configuration_in_json(self._configuration)

        exp_name = setup(data=X)

        best_score = -2
        best_model = None
        for clustering_approach in parameters["include_approach"]:
            model = create_model(clustering_approach, num_clusters=parameters["n_clusters"])
            metrics_df = pull()
            silhouette_score = metrics_df['Silhouette'][0]
            print(f"Silhouette Score {clustering_approach}: {silhouette_score}")

            if silhouette_score > best_score:
                best_score = silhouette_score
                best_model = model


        # Create Dashbord for Clustering (with Streamlit (https://streamlit.io))
        save_directory = self._configuration["dashboard_folder_location"]

        support_dict = {
            'kmeans': ['cluster', 'tsne', 'elbow', 'silhouette', 'distance', 'distribution'],
            'kmodes': ['cluster', 'tsne', 'distribution'],
            'ap': ['cluster', 'tsne', 'distance', 'distribution'],
            'hclust': ['cluster', 'tsne', 'distribution'],
            'birch': ['cluster', 'tsne', 'elbow', 'silhouette', 'distribution'],
            'dbscan': ['cluster', 'tsne', 'distribution'],
            'meanshift': ['cluster', 'tsne', 'distance', 'distribution'],
            'optics': ['cluster', 'tsne', 'distribution'],
            'sc': ['cluster', 'tsne', 'distribution']
        }

        # Erhalte die Plot-Typen basierend auf dem gewählten Clustering-Ansatz
        plot_types = support_dict[clustering_approach]

        figures = []
        current_directory = os.getcwd()
        # print(f"Current working directory: {current_directory}")

        save_directory = self._configuration["dashboard_folder_location"]
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        for plot_type in plot_types:
            if plot_type in ['elbow', 'silhouette', 'distance']:
                pathtoplot = plot_model(best_model, plot=plot_type, save=True)
                plot_filename = os.path.join(current_directory, f'{plot_type}.png')
                dashboard_path = os.path.join(save_directory, f'{plot_type}.png')
                os.rename(pathtoplot, plot_filename)
                os.rename(plot_filename, dashboard_path)
            else:
                pathtoplot = plot_model(best_model, plot=plot_type, save=True)
                plot_filename = os.path.join(current_directory, f'{plot_type}.html')
                dashboard_path = os.path.join(save_directory, f'{plot_type}.html')
                os.rename(pathtoplot, plot_filename)
                os.rename(plot_filename, dashboard_path)

        # print(f"Plots saved to {save_directory}")

        save_model(best_model, os.path.join(self._configuration["result_folder_location"], f'model_pycaret'))
        # Create Clustering Dashboard
        os.environ['BROWSER'] = 'none' # prevents the browser from being launched.

        # Set the relative path to the configuration file.
        relative_config_path = os.path.join(os.getcwd(), 'config')
        # Set the environment variable STREAMLIT_CONFIG_DIR (settings for Streamlit).TODO: Does not work (or gets cached?).
        os.environ['STREAMLIT_CONFIG_DIR'] = relative_config_path

        # Runs on Port 8501
        process = subprocess.Popen(
            ['streamlit', 'run', 'AutoMLs/cluster_dashboard.py', save_directory],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

    def __tabular_regression(self):
        #most likely not working, looks like a copy of the flaml adapter
        """Execute the tabular regression task and export the found model"""
        from pycaret.regression import setup, compare_models, save_model, create_model, finalize_model, tune_model

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration, apply_feature_extration=True)
        X[y.name] = y
        parameters = translate_parameters(":pycaret", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), ppc.parameters)
        automl = setup(data = X, target = y.name)
        best = compare_models(budget_time=self._configuration["configuration"]["runtime_limit"] / 3) #Setup for max 1/3 of time
        model = create_model(best)
        tuned = tune_model(model, **parameters)
        fn_model = finalize_model(tuned)
        save_model(fn_model, os.path.join(self._configuration["result_folder_location"], 'model_pycaret'))
        export_model(PycaretWrapper(fn_model, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')

    def __time_series_forecasting(self):
        #most likely not working, looks like a copy of the flaml adapter
        """Execute the tabular classification task and export the found model"""
        from pycaret.time_series import setup, compare_models, save_model, create_model, finalize_model, tune_model



        parameters = translate_parameters(":pycaret", self._configuration["configuration"]["task"], self._configuration["configuration"].get('parameters', {}), ppc.parameters)
        self._configuration["forecasting_horizon"] = parameters["fh"]
        save_configuration_in_json(self._configuration)

        self.df, test = data_loader(self._configuration)

        X, y = prepare_tabular_dataset(self.df, self._configuration)
        X[y.name] = y
        automl = setup(data = X, target = y.name, fh=parameters["fh"])
        del parameters["fh"]
        best = compare_models(budget_time=self._configuration["configuration"]["runtime_limit"] / 3) #Setup for max 1/3 of time
        model = create_model(best)
        tuned = tune_model(model, **parameters)
        fn_model = finalize_model(tuned)
        save_model(fn_model, os.path.join(self._configuration["result_folder_location"], 'model_pycaret'))
        export_model(PycaretWrapper(fn_model, self._configuration), self._configuration["dashboard_folder_location"], 'dashboard_model.p')
        #export_model(automl, self._configuration["result_folder_location"], 'model_pycaret.p')
