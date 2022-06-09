import logging, json

class Blackboard(object):
    """
    Central blackboard component which acts as the shared / common data structure for all training data.
    """

    def __init__(self, initial_state: dict = {}) -> None:
        self.__log = logging.getLogger()
        self.common_state = initial_state
        self.agents = []
        self.__log.debug('Initialized new blackboard.')

    def RegisterAgent(self, agent):
        self.agents.append(agent)

    def UnregisterAgent(self, agent):
        # TODO
        pass

    def ExportCommonState(self) -> None:
        # TODO: JSON or Python Pickle?
        return json.dumps(self.common_state)