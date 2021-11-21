from AutoMLManager import AutoMLManager


class AutoGluonManager(AutoMLManager):
    name = "AutoGluon"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'AUTOGLUON_SERVICE_HOST'
        automl_service_port = 'AUTOGLUON_SERVICE_PORT'
        automl_default_port = '50057'
        super(AutoGluonManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                               automl_default_port)

    def _generate_process_json(self):
        process_json = super()._generate_process_json()
        process_json.update({"time_budget": self._configuration.timeBudget})
        return process_json
