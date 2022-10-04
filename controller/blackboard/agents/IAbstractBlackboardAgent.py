import logging, collections.abc, os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Blackboard import Blackboard
    from StrategyController import StrategyController

class IAbstractBlackboardAgent():
    """
    Interface representing the functionality any blackboard agent must provide.
    """

    def __init__(self, blackboard: "Blackboard", strategy_controller: "StrategyController", agent_identifier: str) -> None:
        """
        Constructs a new blackboard agent
        ---
        Parameter
        1. blackboard: The blackboard to attach to
        """
        self.agent_identifier = agent_identifier
        self._log = logging.getLogger(self.agent_identifier)
        self._log.setLevel(logging.getLevelName(os.getenv("BLACKBOARD_LOGGING_LEVEL")))
        self._log.debug(f'Initialized blackboard agent: "{self.agent_identifier}"')
        self.strategy_controller = strategy_controller
        self.blackboard = blackboard
        self.blackboard.register_agent(self)

    def can_contribute(self) -> bool:
        """
        Indicates whether the blackboard agent wants to contribute something currently.
        ---
        Return a boolean indicating the status
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
        Helper function that returns the blackboard state under a default key ("blackboard_key") for the agent class.
        """
        if not self.blackboard_key:
            raise NotImplementedError(f'{self.__class__.__name__} has no "blackboard_key" attribute!')
        return self.blackboard.get_state(self.blackboard_key, default)
        
    def update_state(self, update, update_dict_recursive: bool = False):
        """
        Helper function that updates the blackboard state under a default key ("blackboard_key") for the agent class.
        """
        if not self.blackboard_key:
            raise NotImplementedError(f'{self.__class__.__name__} has no "blackboard_key" attribute!')
        return self.blackboard.update_state(self.blackboard_key, update, update_dict_recursive)