import logging, json, collections

class Blackboard(object):
    """
    Central blackboard component which acts as the shared / common data structure for all training data.
    """

    def __init__(self, initial_state: dict = {}) -> None:
        self._log = logging.getLogger('blackboard')
        self._log.setLevel(logging.DEBUG) # FIXME: Remove this line, only for debugging
        self.common_state = initial_state
        self.agents = {}
        self._log.debug('Initialized new blackboard.')

    def GetAgent(self, agent_id):
        return self.agents[agent_id]

    def RegisterAgent(self, agent):
        if agent.agent_id in self.agents:
            raise RuntimeError(f'The agent "{agent.agent_id}" has already been registered on this blackboard!')
        else:
            self.agents[agent.agent_id] = agent
            self._log.debug(f'Registered blackboard agent: "{agent.agent_id}"')

    def UnregisterAgent(self, agent):
        if agent.agent_id not in self.agents:
            raise RuntimeError(f'The agent "{agent.agent_id}" has not been registered on this blackboard!')
        else:
            del self.agents[agent.agent_id]
            self._log.debug(f'Unregistered blackboard agent: "{agent.agent_id}"')
    
    def GetState(self, key, default = None):
        return self.common_state.get(key, default)

    def UpdateState(self, key, update, update_dict_recursive: bool = False):
        if isinstance(update, collections.abc.Mapping) and (key in self.common_state) and update_dict_recursive:
            if isinstance(self.GetState(key), collections.abc.Mapping):
                self.UpdateNestedRecursive(self.GetState(key), update)
            else:
                raise RuntimeError(f'The blackboard state for "{key}" is not a dictionary that may be updated.')
        else:
            self.common_state[key] = update

    def UpdateNestedRecursive(self, parent: dict, update: dict) -> dict:
        """
        Performs a deep (recursive) update on the common state and returns the new state dict.
        """
        for k, v in update.items():
            if isinstance(v, collections.abc.Mapping):
                parent[k] = self.UpdateNestedRecursive(parent.get(k, {}), v)
            else:
                parent[k] = v
        return parent

    def ExportCommonState(self) -> None:
        # TODO: JSON/Python Pickle or persistent DB?
        return json.dumps(self.common_state)