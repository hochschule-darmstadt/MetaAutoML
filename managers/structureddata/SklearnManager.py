from AutoMLManager import AutoMLManager


class SklearnManager(AutoMLManager):
    name = "Autosklearn"

    def __init__(self, configuration, folder_location, session_id):
        automl_service_host = 'SKLEARN_SERVICE_HOST'
        automl_service_port = 'SKLEARN_SERVICE_PORT'
        super(SklearnManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                             session_id)
