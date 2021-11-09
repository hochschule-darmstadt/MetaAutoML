import os
from autoPyTorch import AutoNetClassification
from autoPyTorch.data_management.data_manager import DataManager

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
		In case of AutoPytorch only provide the training file path
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
        model.save("templates/output/model_autopytorch", save_format="tf")
        return

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        autonet = AutoNetClassification(budget_type='epochs', min_budget=1, max_budget=9, num_iterations=1, log_level='info')
        res = autonet.fit(self.__training_data_path, self.__json["configuration"]["target"], epochs=10)
        self.__export_model(res)
        return