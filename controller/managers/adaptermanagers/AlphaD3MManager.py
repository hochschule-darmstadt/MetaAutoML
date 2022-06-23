from AutoMLManager import AutoMLManager


class AlphaD3MManager(AutoMLManager):
    """
    Implementation of the specific AutoMLManager for AlphaD3M
    """
    name = "AlphaD3M"

    def __init__(self, configuration, folder_location, session_id, callback):
        """
        Init a new instance of the specific AutoMLManager
        ---
        Parameter
        1. configuration dictionary
        2. folder location of the dataset
        3. session id to use
        ---
        Return a new specific AutoML Manager
        """
        automl_service_host = 'ALPHAD3M_SERVICE_HOST'
        automl_service_port = 'ALPHAD3M_SERVICE_PORT'
        super(AlphaD3MManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                               session_id, callback)
