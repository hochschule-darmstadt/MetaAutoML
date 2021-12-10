from AutoMLManager import AutoMLManager


class MljarManager(AutoMLManager):
    name = "MLJAR"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'MLJAR_SERVICE_HOST'
        automl_service_port = 'MLJAR_SERVICE_PORT'
        super(MljarManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port)
