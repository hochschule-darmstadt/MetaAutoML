from AutoMLManager import AutoMLManager


class AutoGluonManager(AutoMLManager):
    """
    Implementation of the specific AutoMLManager for AutoGluon
    """
    name = "AutoGluon"

    def __init__(self, configuration, folder_location, session_id):
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
        automl_service_host = 'AUTOGLUON_SERVICE_HOST'
        automl_service_port = 'AUTOGLUON_SERVICE_PORT'
        super(AutoGluonManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                               session_id)
