from AutoMLManager import AutoMLManager


class AutoPyTorchManager(AutoMLManager):
    name = "Auto_PyTorch"

    def __init__(self, configuration, folder_location):
        automl_service_host = 'PYTORCH_SERVICE_HOST'
        automl_service_port = 'PYTORCH_SERVICE_PORT'
        super(AutoPyTorchManager, self).__init__(configuration, folder_location, automl_service_host,
                                                 automl_service_port)
