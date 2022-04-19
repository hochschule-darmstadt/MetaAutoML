from AutoMLManager import AutoMLManager


class AutoCVEManager(AutoMLManager):
    """
    Implementation of the specific AutoMLManager for AutoCVE
    """
    name = "AutoCVE"

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
        automl_service_host = 'AUTOCVE_SERVICE_HOST'
        automl_service_port = 'AUTOCVE_SERVICE_PORT'
        super(AutoCVEManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                             session_id)
