from AutoMLManager import AutoMLManager


class SklearnManager(AutoMLManager):
    name = "Autosklearn"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'SKLEARN_SERVICE_HOST'
        automl_service_port = 'SKLEARN_SERVICE_PORT'
        automl_default_port = '50055'
        super(SklearnManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                             automl_default_port)
