from AutoMLManager import AutoMLManager


class AutoGluonManager(AutoMLManager):
    name = "AutoGluon"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'AUTOGLUON_SERVICE_HOST'
        automl_service_port = 'AUTOGLUON_SERVICE_PORT'
        super(AutoGluonManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port)
