from AbstractTabularDataAutoML import AbstractTabularDataAutoML
from JsonUtil import get_config_property
import pickle
import os


class TabularDataAutoML(AbstractTabularDataAutoML):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of TabularDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        super().__init__(configuration)

    # def __read_training_data(self):
    #     """
    #     Read the training dataset from disk
    #             In case of AutoKeras only provide the training file path
    #     """
    #     self.__training_data_path = os.path.join(
    #         self.__configuration["file_location"], self.__configuration["file_name"])
    #     return

    def __export_model(self, model):
        """
        Export the generated ML model to disk
        ---
        Parameter:
        1. generate ML model
        """
        output_file = os.path.join(get_config_property('output-path'), 'tmp', "alphad3m-model.p")
        with open(output_file, "wb+") as file:
            pickle.dump(model, file)

    def __classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        return

    def __regression(self):
        """
        Execute the regression task
        """
        self.__read_training_data()
        return

    def execute_task(self):
        """
        Execute the ML task
        """
        if self._configuration["task"] == 1:
            self.__classification()
        elif self._configuration["task"] == 2:
            self.__regression()
        else:
            raise ValueError(
                f'{get_config_property("adapter-name")} was called with an invalid task: task=={self._configuration["task"]}. The only valid task is task==1 or task==2'
                )
        