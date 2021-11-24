from AutoMLManager import AutoMLManager


class AutoGluonManager(AutoMLManager):
    name = "autogluon"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'AUTOGLUON_SERVICE_HOST'
        automl_service_port = 'AUTOGLUON_SERVICE_PORT'
        automl_default_port = '50057'
        super(AutoGluonManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                               automl_default_port)
