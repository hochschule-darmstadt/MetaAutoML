import autokeras as ak
from AbstractAdapter import AbstractAdapter
from AdapterUtils import (prepare_tabular_dataset,
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
        self.df = read_tabular_dataset_training_data(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)
        clf = ak.StructuredDataClassifier(overwrite=True,
                                          max_trials=self._max_iter,
                                          # metric=self._configuration['metric'],
                                          seed=42)
                                          
        clf.fit(x=X, y=y)
        self.__export_model(clf, 'model_keras.p')

    def __tabular_regression(self):
        """Execute the regression task"""
        read_tabular_dataset_training_data(self._configuration)
        prepare_tabular_dataset(self._configuration)
        reg = ak.StructuredDataRegressor(overwrite=True,
                                         max_trials=self._max_iter,
                                         # metric=self._configuration['metric'],
                                         seed=42)
        reg.fit(x=self._X, y=self._y)
        self.__export_model(reg, 'model_keras.p')

    # hard coded json for the job somewhere s

    def __image_classification(self):
        train_data, test_data = self.__image_dataset_loader(self)

        clf = ak.ImageClassifier(overwrite=True, 
                                max_trials=self._max_iter,
                                seed=42)
        clf.fit(train_data, epochs=1)

    def __image_regression(self):
        train_data = self.__image_dataset_loader(self)

        clf = ak.ImageClassifier(overwrite=True, 
                                max_trials=self._max_iter,
                                seed=42)
        clf.fit(train_data, epochs=1)

    def __image_dataset_loader(self):
        data_dir = ""

        batch_size = 32
        img_height = 180
        img_width = 180

        train_data = ak.image_dataset_from_directory(
            data_dir,
            # Use 20% data as testing data.
            validation_split=0.2,
            subset="training",
            # Set seed to ensure the same split when loading testing data.
            seed=123,
            image_size=(img_height, img_width),
            batch_size=batch_size,
        )

        test_data = ak.image_dataset_from_directory(
            data_dir,
            validation_split=0.2,
            subset="validation",
            seed=123,
            image_size=(img_height, img_width),
            batch_size=batch_size,
        )

        return train_data, test_data
