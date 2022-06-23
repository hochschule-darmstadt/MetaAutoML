import logging, json

class Blackboard(object):
    """
    Central blackboard component which acts as the shared / common data structure for all training data.
    """

    def __init__(self, initial_state: dict = {}) -> None:
        self.__log = logging.getLogger('blackboard')
        self.common_state = initial_state
        self.agents = {}
        self.__log.debug('Initialized new blackboard.')

    def RegisterAgent(self, agent):
        if agent.agent_id in self.agents:
            raise RuntimeError(f'The agent "{agent.agent_id}" has already been registered on this blackbaord!')
        else:
            self.agents[agent.agent_id] = agent
            self.__log.debug(f'Registered blackboard agent: "{agent.agent_id}"')

    def UnregisterAgent(self, agent):
        if agent.agent_id not in self.agents:
            raise RuntimeError(f'The agent "{agent.agent_id}" has not been registered on this blackboard!')
        else:
            del self.agents[agent.agent_id]
            self.__log.debug(f'Ungegistered blackboard agent: "{agent.agent_id}"')

    def ExportCommonState(self) -> None:
        # TODO: JSON or Python Pickle?
        return json.dumps(self.common_state)