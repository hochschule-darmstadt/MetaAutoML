from AutoMLManager import AutoMLManager


class FLAMLManager(AutoMLManager):
    name = "flaml"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'FLAML_SERVICE_HOST'
        automl_service_port = 'FLAML_SERVICE_PORT'
        automl_default_port = '50056'
        super(FLAMLManager, self).__init__(configuration, folder_location, automl_service_host, automl_service_port,
                                           automl_default_port)

    def _generate_process_json(self):
        process_json = super()._generate_process_json()
        process_json.update({"time_budget": self._configuration.timeBudget})
        return process_json
