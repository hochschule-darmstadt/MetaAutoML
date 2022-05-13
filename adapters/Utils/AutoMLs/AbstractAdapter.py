from abc import ABC, abstractmethod


class AbstractAdapter(ABC):
    """
    Abstract adapter class, implement for every specific adapter
    """
    def __init__(self, configuration: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        # set runtime limit from configuration, if it isn't specified its set to 30s
        self._configuration = configuration
        if self._configuration["runtime_constraints"]["runtime_limit"] > 0:
            self._time_limit = self._configuration["runtime_constraints"]["runtime_limit"]
        else:
            self._time_limit = 30
        self._target = self._configuration["tabular_configuration"]["target"]["target"]
        if self._configuration["runtime_constraints"]["max_iter"] == 0:
            self._max_iter = self._configuration["runtime_constraints"]["max_iter"] = 3

    @abstractmethod
    def start(self):
        """Execute the ML task"""
        pass