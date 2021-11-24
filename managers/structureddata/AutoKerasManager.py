from AutoMLManager import AutoMLManager


class AutoKerasManager(AutoMLManager):
    name = "autokeras"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'AUTOKERAS_SERVICE_HOST'
        automl_service_port = 'AUTOKERAS_SERVICE_PORT'
        automl_default_port = '50052'
        super(AutoKerasManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                               automl_default_port)
