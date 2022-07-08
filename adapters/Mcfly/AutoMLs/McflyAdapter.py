from AbstractAdapter import AbstractAdapter
from AdapterUtils import (
    read_tabular_dataset_training_data,
    read_panel_dataset,
    convert_panel_to_numpy3D,
    prepare_tabular_dataset,
    export_model,
    export_keras_model,
    split_data,
    export_label_binarizer
)
from mcfly.find_architecture import find_best_architecture

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

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == 3:
                self.__time_series_classification()

    def __time_series_classification(self):
        """Execute time series classification task"""
        # self.df = read_panel_dataset_training_data(self._configuration)
        # Get training dataset and the label binarizer for the categorial target variable
        X, y, label_binarizer = read_panel_dataset(self._configuration)
        # Split dataset into train and test
        X_train, X_test, y_train, y_test = split_data(X, y, self._configuration)
        # The Mcfly framework is based on keras lib. That's why it expects train and validation datasets
        X_train, X_val, y_train, y_val = split_data(X_train, y_train, self._configuration)
        # Convert datasets into numpy 3d array
        X_train, y_train_binary = convert_panel_to_numpy3D(X_train, y_train, label_binarizer)
        X_val, y_val_binary = convert_panel_to_numpy3D(X_val, y_val, label_binarizer)

        params = {
            'number_of_models': 1,
            'nr_epochs': 5,
            'subset_size': 100,
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
                number_of_models=params['number_of_models'],
                subset_size=params['subset_size']
            )
        # Train the best model on full dataset
        history = best_model.fit(
            X_train,
            y_train_binary,
            epochs=params['nr_epochs'],
            validation_data=(X_val, y_val_binary),
        )
        # Save the model
        export_keras_model(best_model, 'model_mcfly.p')
        # Save the Label Binarizer
        export_label_binarizer(label_binarizer, 'label_binarizer_mcfly.p')
