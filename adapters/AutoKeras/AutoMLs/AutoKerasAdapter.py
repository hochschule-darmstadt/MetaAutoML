import autokeras as ak
import numpy as np
from AdapterUtils import data_loader, export_model, prepare_tabular_dataset, get_column_with_largest_amout_of_text
import pandas as pd
import json
import os
from JsonUtil import get_config_property
import tensorflow as tf

autokeras_metrics = {
    ":accuracy": tf.keras.metrics.Accuracy(),
    ":area_under_roc_curve": tf.keras.metrics.AUC(),
    ":binary_accuracy": tf.keras.metrics.BinaryAccuracy(),
    ":binary_cross_entropy": tf.keras.metrics.BinaryCrossentropy() ,
    ":binary_intersection_over_union": tf.keras.metrics.BinaryIoU(),
    ":categorical_accuracy": tf.keras.metrics.CategoricalAccuracy(),
    ":categorical_cross_entropy": tf.keras.metrics.CategoricalCrossentropy(),
    ":cosine_similarity": tf.keras.metrics.CosineSimilarity(),
    ":false_negatives": tf.keras.metrics.FalseNegatives(),
    ":false_positives": tf.keras.metrics.FalsePositives(),
    ":hinge": tf.keras.metrics.Hinge(),
    ":kullback_leibler_divergence": tf.keras.metrics.KLDivergence(),
    ":log_cosh_error": tf.keras.metrics.LogCoshError(),
    ":mean": tf.keras.metrics.Mean(),
    ":mean_absolut_percentage_error": tf.keras.metrics.MeanAbsolutePercentageError(),
    ":mean_squared_log_error": tf.keras.metrics.MeanSquaredLogarithmicError(),
    ":mean_tensor": tf.keras.metrics.MeanTensor(),
    ":poission": tf.keras.metrics.Poisson(),
    ":precision": tf.keras.metrics.Precision(),
    ":recall": tf.keras.metrics.Recall(),
    ":root_mean_squared_error": tf.keras.metrics.RootMeanSquaredError(),
    ":sparse_categorical_accuracy": tf.keras.metrics.SparseCategoricalAccuracy(),
    ":sparse_top_k_categorical_accuracy": tf.keras.metrics.SparseTopKCategoricalAccuracy(),
    ":squared_hinge": tf.keras.metrics.SquaredHinge(),
    ":sum":tf.keras.metrics.Sum(),
    ":top_k_categorical_accuracy":tf.keras.metrics.TopKCategoricalAccuracy(),
    ":true_negatives": tf.keras.metrics.TrueNegatives(),
    ":true_positives": tf.keras.metrics.TruePositives(),
    ":mean_sqared_error": tf.keras.metrics.MeanSquaredError(),
    ":mean_absolute_error": tf.keras.metrics.MeanAbsoluteError()
}

autokeras_loss_classification = {
    ":binary_cross_entropy": tf.keras.losses.BinaryCrossentropy(),
    ":categorical_cross_entropy": tf.keras.losses.CategoricalCrossentropy()
}
autokeras_loss_regression = {
    ":mean_squared_error": "mean_squared_error",
}

autokeras_tuner = {
    ":greedy": "greedy",
    ":bayesian":"bayesian",
    ":random": "random",
    ":hyperband": "hyperband"
}


class AutoKerasAdapter:
    """
    Implementation of the AutoML functionality for AutoKeras
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
        metrics, losses, max_trials, tuners, max_model_size = self.translate()
        clf = ak.StructuredDataClassifier(overwrite=True,
                                         max_trials=max_trials,
                                         metrics=metrics,
                                         tuner=tuners,
                                         loss=losses,
                                         max_model_size=max_model_size,
                                          directory=self._configuration["model_folder_location"],
                                          seed=42)

        clf.fit(x=X, y=y, epochs=1)
        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __tabular_regression(self):
        """Execute the tabular regression task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        metrics, losses, max_trials, tuners, max_model_size = self.translate()
        reg = ak.StructuredDataRegressor(overwrite=True,
                                          max_trials=max_trials,
                                         metrics=metrics,
                                         tuner=tuners,
                                         loss=losses,
                                         max_model_size= max_model_size,
                                         directory=self._configuration["model_folder_location"],
                                         seed=42)

        reg.fit(x=X, y=y, epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_classification(self):
        """"Execute image classification task and export the found model"""

        X_train, y_train, X_test, y_test = data_loader(self._configuration)
        metrics, losses, max_trials, tuners, max_model_size = self.translate()
        clf = ak.ImageClassifier(overwrite=True,
                                          max_trials=max_trials,
                                         metrics=metrics,
                                         tuner=tuners,
                                         loss=losses,
                                         max_model_size=max_model_size,
                                        seed=42,
                                        directory=self._configuration["model_folder_location"])

        #clf.fit(train_data, epochs=self._configuration["runtime_constraints"]["epochs"])
        clf.fit(x = X_train, y = y_train, epochs=1)

        export_model(clf, self._configuration["result_folder_location"], 'model_keras.p')

    def __image_regression(self):
        """Execute image regression task and export the found model"""

        X_train, y_train, X_val, y_val = data_loader(self._configuration)
        metrics, losses, max_trials, tuners, max_model_size = self.translate()
        reg = ak.ImageRegressor(overwrite=True,
                                          max_trials=max_trials,
                                         metrics=metrics,
                                         tuner=tuners,
                                         loss=losses,
                                         max_model_size=max_model_size,
                                        seed=42,
                                        directory=self._configuration["model_folder_location"])

        reg.fit(x = X_train, y = y_train, epochs=1)

        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def __text_classification(self):
        """Execute text classifiction task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, self._configuration = get_column_with_largest_amout_of_text(self.df, self._configuration)
        X, y = prepare_tabular_dataset(X, self._configuration)
        metrics, losses, max_trials, tuners, max_model_size = self.translate()
        reg = ak.TextClassifier(overwrite=True,
                                # NOTE: bert models will fail with out of memory errors
                                #   even with 32GB GB RAM
                                # the first model is a non-bert transformer
                                max_trials=max_trials,
                                metrics=metrics,
                                tuner=tuners,
                                loss=losses,
                                max_model_size= max_model_size,
                                seed=42,
                                directory=self._configuration["model_folder_location"])


        reg.fit(x = np.array(X).astype(np.unicode_), y = np.array(y), epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')


    def __text_regression(self):
        """Execute text regression task and export the found model"""
        self.df, test = data_loader(self._configuration)
        X, self._configuration = get_column_with_largest_amout_of_text(self.df, self._configuration)
        X, y = prepare_tabular_dataset(X, self._configuration)
        metrics, losses, max_trials, tuners, max_model_size = self.translate()
        reg = ak.TextClassifier(overwrite=True,
                                          max_trials=max_trials,
                                         metrics=metrics,
                                         tuner=tuners,
                                         loss=losses,
                                         max_model_size=max_model_size,
                                seed=42,
                                directory=self._configuration["model_folder_location"])

        reg.fit(x = np.array(X), y = np.array(y), epochs=1)
        export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')


    def __time_series_forecasting(self):
        """Execute time series forecasting task and export the found model"""

        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        #TODO convert dataframe to float
        metrics, losses, max_trials, tuners, max_model_size = self.translate()
        reg = ak.TimeseriesForecaster(overwrite=True,
                                          max_trials=max_trials,
                                         metrics=metrics,
                                         tuner=tuners,
                                         loss=losses,
                                         max_model_size=max_model_size,
                                          lookback=1,

                                seed=42,
                                directory=self._configuration["model_folder_location"])

        X = X.bfill().ffill()  # makes sure there are no missing values
        y = y.bfill().ffill()  # makes sure there are no missing values
        #Loopback must be dividable by batch_size else time seires will crash
        reg.fit(x = X, y = y, epochs=1, batch_size=1)
        model = reg.export_model()
        model.save(os.path.join(self._configuration["result_folder_location"], 'model_keras'), save_format="tf")
        #export_model(reg, self._configuration["result_folder_location"], 'model_keras.p')

    def get_column_with_largest_amout_of_text(self, X: pd.DataFrame):
        """
        Find the column with the most text inside,
        because AutoKeras only supports training with one feature
        Args:
            X (pd.DataFrame): The current X Dataframe

        Returns:
            pd.Dataframe: Returns a pandas Dataframe with the column with the most text inside
        """
        column_names = []
        target = ""
        dict_with_string_length = {}

        #First get only columns that will be used during training
        for column, dt in self._configuration["dataset_configuration"]["schema"].items():
            if dt.get("role_selected", "") == ":ignore" or dt.get("role_selected", "") == ":index" or dt.get("role_selected", "") == ":target":
                continue
            column_names.append(column)

        #Check the used columns by dtype object (== string type) and get mean len to get column with longest text
        for column_name in column_names:
            if(X.dtypes[column_name] == object):
                newlength = X[column_name].str.len().mean()
                dict_with_string_length[column_name] = newlength
        max_value = max(dict_with_string_length, key=dict_with_string_length.get)

        #Remove the to be used text column from the list of used columns and set role ignore as Autokeras can only use one input column for text tasks
        column_names.remove(max_value)
        for column_name in column_names:
            self._configuration["dataset_configuration"]["schema"][column_name]["role_selected"] = ":ignore"

        return X


    def save_configuration_in_json(self):
        """ serialize dataset_configuration to json string and save the the complete configuration in json file
            to habe the right datatypes available for the evaluation
        """
        self._configuration['dataset_configuration'] = json.dumps(self._configuration['dataset_configuration'])
        with open(os.path.join(self._configuration['job_folder_location'], get_config_property("job-file-name")), "w+") as f:
            json.dump(self._configuration, f)


    def __read_parameter(self, intersect_parameter, automl_parameter, default=[None]):
        parameters = self._configuration["configuration"].get('parameters', {})
        value = list()
        try:
            value = parameters[intersect_parameter]['values']
        except:
            pass
        try:
            values2 = parameters[automl_parameter]['values']
            for para in values2:
                if para not in value:
                    value.append(para)
        except:
            pass
        if len(value) == 0:
            return default
        else:
            return value

    def translate(self):
        parameters = self._configuration["configuration"].get('parameters', {})
        metrics = []
        #try to get the metric values from configuration, if not available use accuracy
        try:
            metric_parameters = parameters[':metric']['values']
            for metric_parameter in metric_parameters:
                metrics.append(autokeras_metrics.get(metric_parameter, 'accuracy'))
        except:
            metrics = ['accuracy']

        #try to get the loss values from configuration, if not available use binary_crossentropy for classification and mean_squared_error for regression
        try:
            loss_parameters = parameters[':loss']['values']
            if self._configuration['configuration']['task'] == ":text_classification" or self._configuration['configuration']['task'] == ":tabular_classification" or self._configuration['configuration']['task'] == ":image_classification" :
                loss = autokeras_loss_classification.get(loss_parameters[0], 'binary_cross_entropy')
            if self._configuration['configuration']['task'] == ":tabular_regression" or self._configuration['configuration']['task'] == ":text_regression" or self._configuration['configuration']['task'] == ":image_regression"  :
                loss = autokeras_loss_regression.get(loss_parameters[0], 'mean_squared_error')
        except:
            if self._configuration['configuration']['task'] == ":text_classification" or self._configuration['configuration']['task'] == ":tabular_classification" or self._configuration['configuration']['task'] == ":image_classification" :
                loss = 'binary_crossentropy'
            if self._configuration['configuration']['task'] == ":tabular_regression" or self._configuration['configuration']['task'] == ":text_regression" or self._configuration['configuration']['task'] == ":image_regression"  :
                loss = 'mean_squared_error'
        #try to get the max_trial from configuration, if not available use 3
        try:
            max_trials_parameter = int(parameters[':max_trials_autokeras']['values'][0])
        except:
            max_trials_parameter = 3

        #try to get the tuner from configuration, if not available use None
        try:
            tuner_parameters = parameters[':tuner_autokeras']['values']
            tuner = autokeras_tuner.get(tuner_parameters[0], None)
        except:
            tuner = None

        #try to get the max_model_size from configuration, if not available use None
        try:
            #Set max model size to None if it is 0, requires a high number to work correctly NOT FOR BEGINNERS
            max_model_size_parameter = int(parameters[':max_model_size_autokeras']['values'][0]) if int(parameters[':max_model_size_autokeras']['values'][0]) > 0 else None
        except:
            max_model_size_parameter = None


        return metrics, loss, max_trials_parameter, tuner, max_model_size_parameter
