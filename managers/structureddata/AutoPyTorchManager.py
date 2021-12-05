from AutoMLManager import AutoMLManager


class AutoPyTorchManager(AutoMLManager):
    name = "Auto_PyTorch"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'AUTOPYTORCH_SERVICE_HOST'
        automl_service_port = 'AUTOPYTORCH_SERVICE_PORT'
        super(AutoPyTorchManager, self).__init__(configuration, folder_location, automl_service_host,
                                                 automl_service_port)
