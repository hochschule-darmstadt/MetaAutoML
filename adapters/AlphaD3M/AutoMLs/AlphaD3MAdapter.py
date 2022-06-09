import d3m_interface as d3mi


from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data


class AlphaD3MAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for AlphaD3MAdapter
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of AlphaD3MAdapter
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        super(AlphaD3MAdapter, self).__init__(configuration)

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == 1:
                self.__tabular_classification()

    def __tabular_classification(self):
        """Execute the classification task"""
        self.df = read_tabular_dataset_training_data(self._configuration)
        print(self.df)
