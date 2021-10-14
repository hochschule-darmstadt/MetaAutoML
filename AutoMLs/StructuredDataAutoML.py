import os
import autokeras as ak
from tensorflow.keras.models import load_model

class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """
    def __init__(self, json: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        self.__json = json
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
		In case of AutoKeras only provide the training file path
        """
        self.__training_data_path = os.path.join(self.__json["file_location"], self.__json["file_name"])
        return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        model = model.export_model()
        model.summary()
        model.save("templates/output/model_autokeras", save_format="tf")
        return

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        clf = ak.StructuredDataClassifier(overwrite=True, max_trials=3, seed=42)
        clf.fit(self.__training_data_path, self.__json["configuration"]["target"], epochs=10)
        self.__export_model(clf)
        return

    def regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        reg = ak.StructuredDataRegressor(overwrite=True, max_trials=3)
        reg.fit(self.__training_data_path, self.__json["configuration"]["target"], epochs=10)
        self.__export_model(reg)
        return