from AutoMLManager import AutoMLManager


class SklearnManager(AutoMLManager):
    """
    Implementation of the specific AutoMLManager for AutoSklearn
    """
    name = "Autosklearn"

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
        automl_service_host = 'SKLEARN_SERVICE_HOST'
        automl_service_port = 'SKLEARN_SERVICE_PORT'
        super(SklearnManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                             session_id, callback)
