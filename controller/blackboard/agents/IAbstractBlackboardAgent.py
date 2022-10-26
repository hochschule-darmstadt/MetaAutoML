import logging, collections.abc, os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Blackboard import Blackboard
    from StrategyController import StrategyController

class IAbstractBlackboardAgent():
    """
    Interface representing the functionality any blackboard agent must provide.
    """

    def __init__(self, blackboard: "Blackboard", strategy_controller: "StrategyController", agent_id: str) -> None:
        """
        Constructs a new blackboard agent
        
        Args:
            blackboard (Blackboard): The blackboard to attach to.
            controller (StrategyController): The strategy controller that is invoking this agent.
            agent_id (str): A unique identifier for the agent.
        """
        self.agent_id = agent_id
        self._log = logging.getLogger(self.agent_id)
        self._log.setLevel(logging.getLevelName(os.getenv("BLACKBOARD_LOGGING_LEVEL")))
        self._log.debug(f'Initialized blackboard agent: "{self.agent_id}"')
        self.strategy_controller = strategy_controller
        self.blackboard = blackboard
        self.blackboard.register_agent(self)

    def can_contribute(self) -> bool:
        """
        Indicates whether the blackboard agent wants to contribute something currently.
        
        Returns:
            bool: A boolean indicating wheter the agent wants to contribute something at the current state.
        """
        raise NotImplementedError('Not implemented!')

    def do_contribute(self) -> any:
        """
        Performs the contribution to the shared blackboard.
        """
        raise NotImplementedError('Not implemented!')

    def unregister(self):
        """
        Unregisters the agent itself from the blackboard.
        """
        self.blackboard.unregister_agent(self)

    def get_state(self, default = None):
        """
        Helper function that returns the current blackboard state under a default key ("blackboard_key") for the agent class.
        
        Args:
            1default (any): A fallback value that is returned if the specified key does not exist.
        """
        if not self.blackboard_key:
            raise NotImplementedError(f'{self.__class__.__name__} has no "blackboard_key" attribute!')
        return self.blackboard.get_state(self.blackboard_key, default)
        
    def update_state(self, update, update_dict_recursive: bool = False):
        """
        Helper function that updates the current blackboard state under a default key ("blackboard_key") for the agent class.
        
        Args:
            update (dict|any): The value to set at the default key ("blackboard_key") for the agent class.
            update_dict_recursive (bool): If enabled and the "update" is a dictionary, the state is updated via a recursive merge.
        """
        if not self.blackboard_key:
            raise NotImplementedError(f'{self.__class__.__name__} has no "blackboard_key" attribute!')
        return self.blackboard.update_state(self.blackboard_key, update, update_dict_recursive)