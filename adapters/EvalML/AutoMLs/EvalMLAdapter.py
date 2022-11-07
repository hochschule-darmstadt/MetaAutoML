import os

from AbstractAdapter import AbstractAdapter
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader
from JsonUtil import get_config_property

# TODO implement
class EvalMLAdapter(AbstractAdapter):
    """Implementation of the AutoML functionality for EvalML

    Args:
        AbstractAdapter (_type_): _description_
    """

    def __init__(self, configuration: dict):
        """Init a new instance of EvalMLAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        super(EvalMLAdapter, self).__init__(configuration)

    def start(self):
        """Start the correct ML task functionality of EvalML"""
        raise NotImplementedError("Correct ML task should be implemented!")
