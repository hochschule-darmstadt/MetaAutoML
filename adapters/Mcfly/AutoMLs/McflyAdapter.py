from mcfly.find_architecture import train_models_on_samples
from mcfly.modelgen import generate_models
from sklearn.preprocessing import OneHotEncoder
from AbstractAdapter import AbstractAdapter
from JsonUtil import get_config_property
import tensorflow as tf
import numpy as np
import os
from McflyUtils import (
    convert_longitudinal_to_numpy,
    read_longitudinal_dataset,
    export_one_hot_encoder,
    estimate_num_models,
    export_keras_model,
    get_class_weights,
    split_dataset,
    get_subset
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
        # Get training dataset
        X, y = read_longitudinal_dataset(self._configuration)
        X = np.swapaxes(X, 1, 2)

        # Create an one hot encoder for the categorical target variable
        one_hot_encoder = OneHotEncoder()
        one_hot_encoder.fit(y.reshape(-1, 1))
        y_binary = one_hot_encoder.transform(y.reshape(-1, 1)).toarray()

        # Split dataset into train and test
        # The Mcfly framework is based on the tensorflow library.
        # That's why it expects train and validation datasets
        X_train, X_test, y_train_binary, y_test_binary = split_dataset(X, y_binary, self._configuration)
        X_train, X_val, y_train_binary, y_val_binary = split_dataset(X_train, y_train_binary, self._configuration)

        # Prepare parameter values to estimate the number of ml models
        num_epochs = 30
        num_instances = X_train.shape[0]
        series_length = X_train.shape[1]
        num_channels = X.shape[2]
        runtime_seconds = int(self._configuration["runtime_constraints"]["runtime_limit"] * 60)

        # Estimate the number of ml models using linear regression
        num_models = estimate_num_models([
            num_epochs, num_instances, series_length, num_channels, runtime_seconds
        ])

        model_types = ['CNN', 'ResNet', 'InceptionTime']
        num_models = max(len(model_types), num_models)
        # Limit the max amount of generated models to avoid the OutOfMemory exception and longer training duration
        num_models = max(15, num_models)

        # Generate new models
        metric_key = "accuracy"
        models = generate_models(
            X_train.shape,
            y_train_binary.shape[1],
            number_of_models=num_models,
            model_types=model_types,
            metrics=[metric_key]
        )

        # Fit the generated models on a subset of data (100 rows)
        # and find the best deep learning architecture
        X_train_subset, y_train_subset = get_subset(
            x_data=X_train,
            y_data=y_train_binary,
            num_classes=len(one_hot_encoder.categories_[0]),
            subset_size=100
        )

        X_val_subset, y_val_subset = get_subset(
            x_data=X_val,
            y_data=y_val_binary,
            num_classes=len(one_hot_encoder.categories_[0]),
            subset_size=100
        )

        class_weights = get_class_weights(y_binary)

        print("Starting model training")
        history, val_metrics, val_losses = train_models_on_samples(
            X_train=X_train_subset,
            y_train=y_train_subset,
            X_val=X_val_subset,
            y_val=y_val_subset,
            models=models,
            nr_epochs=num_epochs,
            verbose=True,
            subset_size=None,
            class_weight=class_weights
        )

        best_model_index = np.argmax(val_metrics[metric_key])
        best_model, best_params, best_model_type = models[best_model_index]

        print("Best model type:", best_model_type)

        print("Training the best model on full training-dataset ...")
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=int(num_epochs/10)
        )

        history = best_model.fit(
            X_train,
            y_train_binary,
            epochs=num_epochs,
            validation_data=(X_val, y_val_binary),
            callbacks=[early_stopping],
            class_weight=class_weights,
        )

        # Saving the best model
        export_keras_model(best_model,
                           self._configuration["result_folder_location"],
                           'model_mcfly.p')

        # Saving the fitted instance of OneHotEncoder
        export_one_hot_encoder(one_hot_encoder,
                               self._configuration["result_folder_location"],
                               'one_hot_encoder_mcfly.p')
