import os

import autokeras as ak
import tensorflow as tf
from AbstractAdapter import AbstractAdapter
from AdapterUtils import (export_model, prepare_tabular_dataset,
                          read_tabular_dataset_training_data)
from JsonUtil import get_config_property


class AutoKerasAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for AutoKeras
    """
    def __init__(self, configuration: dict):
        """
        Init a new instance of AutoKerasAdapter
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        super(AutoKerasAdapter, self).__init__(configuration)
        self._result_path = os.path.join(get_config_property("output-path"), self._configuration["session_id"])

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == 1:
                self.__tabular_classification()
            elif self._configuration["task"] == 2:
                self.__tabular_regression()
            elif self._configuration["task"] == 3:
                self.__image_classification()
            elif self._configuration["task"] == 4:
                self.__image_regression()

    def __tabular_classification(self):
        """Execute the classification task"""
        self.df, test = self.__data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        clf = ak.StructuredDataClassifier(overwrite=True,
                                          max_trials=self._max_iter,
                                          # metric=self._configuration['metric'],
                                          directory=self._result_path,
                                          seed=42)
                                          
        clf.fit(x=X, y=y)
        export_model(clf, self._configuration["session_id"], 'model_keras.p')

    def __tabular_regression(self):
        """Execute the regression task"""
        self.df, test = self.__data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        reg = ak.StructuredDataRegressor(overwrite=True,
                                         max_trials=self._max_iter,
                                         # metric=self._configuration['metric'],
                                         directory=self._result_path,
                                         seed=42)
        reg.fit(x=X, y=y)
        self.__export_model(reg, self._configuration["session_id"], 'model_keras.p')

    
    # hard coded json for the job somewhere

    def __image_classification(self):
        """"Execute image classification task"""
        train_data, test_data = self.__read_image_dataset(self._configuration)

        clf = ak.ImageClassifier(overwrite=True, 
                                max_trials=self._configuration["runtime_constraints"]["max_iter"],
                                seed=42,
                                directory=self._result_path)

        clf.fit(train_data, epochs=1)
        print(clf.evaluate(test_data))

    def __image_regression(self):
        """Execute image regression task"""
        train_data, test_data = self.__image_dataset_loader(self._configuration)

        reg = ak.ImageRegressor(overwrite=True, 
                                max_trials=self._configuration["runtime_constraints"]["max_iter"],
                                seed=42,
                                directory=self._result_path)
                                
                                
        reg.fit(train_data, epochs=1)
        print(reg.evaluate(test_data))

    def __read_image_dataset(self, json_configuration):
        """Reads image data and creates AutoKeras specific structure/sets"""

        # Read from URL if not in cache_dir. URL/Filename need to be specified
        local_file_path = tf.keras.utils.get_file(
            origin=json_configuration["file_location"], 
            fname="image_data", 
            cache_dir=os.path.abspath(os.path.join("app-data")), 
            extract=True
        )

        local_dir_path = os.path.dirname(local_file_path)
        data_dir = os.path.join(local_dir_path, json_configuration["file_name"])

        train_data, test_data = None

        if(json_configuration["test_configuration"]["split_ratio"] > 0):
            train_data = ak.image_dataset_from_directory(
                data_dir,
                validation_split=json_configuration["test_configuration"]["split_ratio"],
                subset="training",
                seed=123,
                image_size=(json_configuration["test_configuration"]["image_height"], json_configuration["test_configuration"]["image_width"]),
                batch_size=json_configuration["test_configuration"]["batch_size"],
            )

            test_data = ak.image_dataset_from_directory(
                data_dir,
                validation_split=json_configuration["test_configuration"]["split_ratio"],
                subset="validation",
                seed=123,
                image_size=(json_configuration["test_configuration"]["image_height"], json_configuration["test_configuration"]["image_width"]),
                batch_size=json_configuration["test_configuration"]["batch_size"],
            )
        else:
            train_data = ak.image_dataset_from_directory(
                os.path.join(data_dir, "train"),
                json_configuration["test_configuration"]["batch_size"]
            )

            test_data = ak.image_dataset_from_directory(
                os.path.join(data_dir, "test"), 
                shuffle=False, 
                batch_size=json_configuration["test_configuration"]["batch_size"]
            )
    @staticmethod
    def __data_loader(config):
        train_data = None
        test_data = None

        if config["task"] == 1:
            train_data, test_data = read_tabular_dataset_training_data(config)
        elif config["task"] == 2:
            train_data, test_data = read_tabular_dataset_training_data(config)
        elif config["task"] == 3:
            train_data, test_data = None
        elif config["task"] == 4:
            train_data, test_data = None
        elif config["task"] == 5:
            train_data, test_data = None

        return train_data, test_data
