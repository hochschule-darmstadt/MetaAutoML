import numpy as np
from AbstractAdapter import AbstractAdapter
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader


class TPOTAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for TPOT
    """
    def __init__(self, configuration: dict):
        """Init a new instance of TPOTAdapter

        Args:
            configuration (dict): Dictonary holding the training configuration
        """
        super(TPOTAdapter, self).__init__(configuration)

    def start(self):
        """Start the correct ML task functionality of TPOT"""
        #if True:
            

    
    