import logging, json, collections, os
from threading import Lock

from IAbstractBlackboardAgent import IAbstractBlackboardAgent

class Blackboard():
    """
    Central blackboard component which acts as the shared / common data structure for all training data.
    """

    def __init__(self, initial_state: dict = None) -> None:
        self._log = logging.getLogger('blackboard')
        self._log.setLevel(logging.getLevelName(os.getenv("BLACKBOARD_LOGGING_LEVEL")))
        self.__lock = Lock()
        self.common_state = initial_state if initial_state is not None else dict()
        self.agents: dict[str, IAbstractBlackboardAgent] = {}
        self._log.debug('Initialized new blackboard.')

    def get_agent(self, agent_id) -> IAbstractBlackboardAgent:
        return self.agents[agent_id]

    def register_agent(self, agent: IAbstractBlackboardAgent):
        if agent.agent_id in self.agents:
            raise RuntimeError(f'The agent "{agent.agent_id}" has already been registered on this blackboard!')
        else:
            self.agents[agent.agent_id] = agent
            self._log.debug(f'Registered blackboard agent: "{agent.agent_id}"')

    def unregister_agent(self, agent: IAbstractBlackboardAgent):
        if agent.agent_id not in self.agents:
            raise RuntimeError(f'The agent "{agent.agent_id}" has not been registered on this blackboard!')
        else:
            del self.agents[agent.agent_id]
            self._log.debug(f'Unregistered blackboard agent: "{agent.agent_id}"')
    
    def get_state(self, key = None, default = None):
        with self.__lock:
            if key is None:
                state = self.common_state
            else:
                state = self.common_state.get(key, default)
        return state

    def update_state(self, key, update, update_dict_recursive: bool = False):
        with self.__lock:
            if isinstance(update, collections.abc.Mapping) and (key in self.common_state) and update_dict_recursive:
                if isinstance(self.common_state.get(key), collections.abc.Mapping):
                    self.update_nested_recursive(self.common_state.get(key), update)
                else:
                    raise RuntimeError(f'The blackboard state for "{key}" is not a dictionary that may be updated.')
            else:
                self.common_state[key] = update

    def update_nested_recursive(self, parent: dict, update: dict) -> dict:
        """
        Performs a deep (recursive) update on the common state and returns the new state dict.
        """
        for k, v in update.items():
            if isinstance(v, collections.abc.Mapping):
                parent[k] = self.update_nested_recursive(parent.get(k, {}), v)
            else:
                parent[k] = v
        return parent

    def export_common_state(self) -> None:
        # TODO: JSON/Python Pickle or persistent DB?
        return json.dumps(self.common_state)