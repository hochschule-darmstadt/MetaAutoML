from abc import ABC, abstractmethod

class AbstractAdapter(ABC):
    """
    Abstract adapter class, implemented by every specific adapter implementation providing the base functionality shared by all adapters
    """
    def __init__(self, configuration: dict):
        """Initialize a new AbstractAdapter instance

        Args:
            configuration (dict): training configuration dictonary holding all informations set during the wizard process
        """
        # set runtime limit from configuration, if it isn't specified its set to 30s
        self._configuration = configuration
        if self._configuration["configuration"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["configuration"]["runtime_limit"]
        else:
            self._time_limit = 30
        if self._configuration["configuration"]["task"] == ":tabular_classification" or self._configuration["configuration"]["task"] == ":tabular_regression" or self._configuration["configuration"]["task"] == ":text_classification" or self._configuration["configuration"]["task"] == ":text_regression":
            self._target = self._configuration["configuration"]["target"]

    @abstractmethod
    def start(self):
        """Start the AutoML process
        """
        pass