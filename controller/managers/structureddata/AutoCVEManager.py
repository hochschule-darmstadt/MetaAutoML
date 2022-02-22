from AutoMLManager import AutoMLManager


class AutoCVEManager(AutoMLManager):
    name = "AutoCVE"

    def __init__(self, configuration, folder_location, session_id):
        automl_service_host = 'AUTOCVE_SERVICE_HOST'
        automl_service_port = 'AUTOCVE_SERVICE_PORT'
        super(AutoCVEManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                             session_id)
