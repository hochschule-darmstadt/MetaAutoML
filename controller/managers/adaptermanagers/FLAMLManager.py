from AutoMLManager import AutoMLManager


class FLAMLManager(AutoMLManager):
    """
    Implementation of the specific AutoMLManager for FLAML
    """
    name = "FLAML"

    def __init__(self, configuration, folder_location, session_id, callback):
        automl_service_host = 'FLAML_SERVICE_HOST'
        automl_service_port = 'FLAML_SERVICE_PORT'
        super(FLAMLManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                           session_id, callback)
