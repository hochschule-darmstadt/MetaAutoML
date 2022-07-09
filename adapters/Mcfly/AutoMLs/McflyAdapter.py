from mcfly.find_architecture import find_best_architecture
from sklearn.preprocessing import LabelBinarizer
from AbstractAdapter import AbstractAdapter
from JsonUtil import get_config_property
import numpy as np
import os
from AdapterUtils import (
    convert_longitudinal_to_numpy,
    read_longitudinal_dataset,
    export_label_binarizer,
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
        self._result_path = os.path.join(get_config_property("output-path"), self._configuration["session_id"])

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == ":time_series_classification":
                self.__time_series_classification()

    def __time_series_classification(self):
        """Execute time series classification task"""
        # self.df = read_panel_dataset_training_data(self._configuration)
        # Get training dataset and the label binarizer for the categorial target variable
        df_train, df_test = read_longitudinal_dataset(self._configuration)
        TARGET_col = "target"
        label_binarizer = LabelBinarizer()
        label_binarizer.fit(np.concatenate([df_train[TARGET_col], df_test[TARGET_col]]))

        # Split dataset into train and test
        # The Mcfly framework is based on keras lib. That's why it expects train and validation datasets
        df_train, df_val = split_dataset(df_train, self._configuration)

        X_train, y_train = df_train.drop([TARGET_col], axis=1), df_train[TARGET_col]
        X_val, y_val = df_val.drop([TARGET_col], axis=1), df_val[TARGET_col]

        # Convert datasets into numpy 3d array
        X_train, y_train_binary = convert_longitudinal_to_numpy(X_train, y_train, label_binarizer)
        X_train = np.swapaxes(X_train, 1, 2)

        X_val, y_val_binary = convert_longitudinal_to_numpy(X_val, y_val, label_binarizer)
        X_val = np.swapaxes(X_val, 1, 2)

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
        export_keras_model(best_model, self._configuration["session_id"], 'model_mcfly.p')
        # Save the Label Binarizer
        export_label_binarizer(label_binarizer, self._configuration["session_id"], 'label_binarizer_mcfly.p')
