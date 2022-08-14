from mcfly.find_architecture import find_best_architecture
from sklearn.preprocessing import OneHotEncoder
from AbstractAdapter import AbstractAdapter
from JsonUtil import get_config_property
import numpy as np
import os
from McflyUtils import (
    convert_longitudinal_to_numpy,
    read_longitudinal_dataset,
    export_one_hot_encoder,
    export_keras_model,
    split_dataset,
)


class McflyAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for Mcfly
    """
    def __init__(self, configuration: dict):
        """
        Init a new instance of McflyAdapter
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        super(McflyAdapter, self).__init__(configuration)
        # self._result_path = os.path.join(get_config_property("output-path"), self._configuration["session_id"])
        self._result_path = configuration["model_folder_location"]

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == ":time_series_classification":
                self.__time_series_classification()

    def __time_series_classification(self):
        """Execute time series classification task"""
        # self.df = read_panel_dataset_training_data(self._configuration)
        # Get training dataset and the one hot encoder for the categorical target variable
        # df_train, df_test = read_longitudinal_dataset(self._configuration)
        X, y = read_longitudinal_dataset(self._configuration)
        X = np.swapaxes(X, 1, 2)

        one_hot_encoder = OneHotEncoder()
        one_hot_encoder.fit(y.reshape(-1, 1))
        y_binary = one_hot_encoder.transform(y.reshape(-1, 1)).toarray()

        # Split dataset into train and test
        # The Mcfly framework is based on keras lib. That's why it
        # expects train and validation datasets
        X_train, X_test, y_train_binary, y_test_binary = split_dataset(X, y_binary, self._configuration)
        X_train, X_val, y_train_binary, y_val_binary = split_dataset(X_train, y_train_binary, self._configuration)

        params = {
            'number_of_models': 1,
            'nr_epochs': 5,
            'nr_rows': X_train.shape[0],
            'nr_columns': X_train.shape[1]
        }

        # Fit models on a subset of data (100 rows) and find the best deep learning architecture
        best_model, best_params, best_model_type, knn_acc = \
            find_best_architecture(
                X_train=X_train,
                y_train=y_train_binary,
                X_val=X_val,
                y_val=y_val_binary,
                nr_epochs=params['nr_epochs'],
                number_of_models=params['number_of_models']
            )
        # Train the best model on full dataset
        history = best_model.fit(
            X_train,
            y_train_binary,
            epochs=params['nr_epochs'],
            validation_data=(X_val, y_val_binary),
        )
        # Save the model
        export_keras_model(best_model,
                           self._configuration["result_folder_location"],
                           'model_mcfly.p')
        # Save the One Hot Encoder instance
        export_one_hot_encoder(one_hot_encoder,
                               self._configuration["result_folder_location"],
                               'one_hot_encoder_mcfly.p')
