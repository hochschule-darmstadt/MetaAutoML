import logging, pickle, collections, os
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
        """
        Retrieves a registered blackboard agent by its unique identifier.
        
        Args:
            agent_id (str): The ID of the agent to retrieve.

        Returns:
            IAbstractBlackboardAgent: The respective blackboard agent instantiation.
        """
        return self.agents[agent_id]

    def register_agent(self, agent: IAbstractBlackboardAgent):
        """
        Registers a given agent to the blackboard.
        
        Args:
            agent (IAbstractBlackboardAgent): An instantiation of a blackboard agent that should be registered.
        """
        if agent.agent_id in self.agents:
            raise RuntimeError(f'The agent "{agent.agent_id}" has already been registered on this blackboard!')
        else:
            self.agents[agent.agent_id] = agent
            self._log.debug(f'Registered blackboard agent: "{agent.agent_id}"')

    def unregister_agent(self, agent: IAbstractBlackboardAgent):
        """
        Unregisters a given agent from the blackboard.
        
        Args:
            agent (IAbstractBlackboardAgent): An instantiation of a blackboard agent that should be unregistered.
        """
        if agent.agent_id not in self.agents:
            raise RuntimeError(f'The agent "{agent.agent_id}" has not been registered on this blackboard!')
        else:
            del self.agents[agent.agent_id]
            self._log.debug(f'Unregistered blackboard agent: "{agent.agent_id}"')
    
    def get_state(self, key = None, default = None):
        """
        Helper function that returns the current blackboard state at a certain subkey.
        
        Args:
            key (any): The respective key at which the value should be retrieved.
            default (any): A fallback value that is returned if the specified key does not exist.

        Returns:
            any: The value that is currently set at the given key (or the default value).
        """
        with self.__lock:
            if key is None:
                state = self.common_state
            else:
                state = self.common_state.get(key, default)
        return state

    def update_state(self, key, update, update_dict_recursive: bool = False):
        """
        Helper function that updates the current blackboard state at a certain subkey.
        
        Args:
            key (any): The respective key at which the value should be set.
            update (dict|any): The value to set at the respective key.
            update_dict_recursive (bool): If enabled and the "update" is a dictionary, the state is updated via a recursive merge.
        """
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
        
        Args:
            parent (dict): The parent dictionary that is the base for the update.
            update (dict): The update dictionary that is merged with the parent.

        Returns:
            dict: The merged dictionary.
        """
        for k, v in update.items():
            if isinstance(v, collections.abc.Mapping):
                parent[k] = self.update_nested_recursive(parent.get(k, {}), v)
            else:
                parent[k] = v
        return parent

    def export_common_state(self) -> bytes:
        """
        Returns the current blackboard state in a portable serialized (pickled) representation.
        
        Returns:
            bytes: The pickled binary data.
        """
        return pickle.dumps(self.common_state)