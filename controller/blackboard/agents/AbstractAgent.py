import logging, collections.abc
from ..Blackboard import Blackboard
from ..Controller import StrategyController

class IAbstractBlackboardAgent():
    """
    Interface representing the functionality any blackboard agent must provide.
    """

    def __init__(self, blackboard: Blackboard, controller: StrategyController, agent_id: str) -> None:
        """
        Constructs a new blackboard agent
        ---
        Parameter
        1. blackboard: The blackboard to attach to
        """
        self.agent_id = agent_id
        self._log = logging.getLogger(self.agent_id)
        self._log.debug(f'Initialized blackboard agent: "{self.agent_id}"')
        self.controller = controller
        self.blackboard = blackboard
        self.blackboard.RegisterAgent(self)

    def CanContribute(self) -> bool:
        """
        Indicates whether the blackboard agent wants to contribute something currently.
        ---
        Return a boolean indicating the status
        """
        raise NotImplementedError('Not implemented!')

    def DoContribute(self) -> any:
        """
        Performs the contribution to the shared blackboard.
        """
        raise NotImplementedError('Not implemented!')

    def Unregister(self):
        """
        Unregisters the agent itself from the blackboard.
        """
        self.blackboard.UnregisterAgent(self)

    def GetState(self, default = None):
        """
        Helper function that returns the blackboard state under a default key ("blackboard_key") for the agent class.
        """
        if not self.blackboard_key:
            raise NotImplementedError(f'{self.__class__.__name__} has no "blackboard_key" attribute!')
        return self.blackboard.GetState(self.blackboard_key, default)
        
    def UpdateState(self, update, update_dict_recursive: bool = False):
        """
        Helper function that updates the blackboard state under a default key ("blackboard_key") for the agent class.
        """
        if not self.blackboard_key:
            raise NotImplementedError(f'{self.__class__.__name__} has no "blackboard_key" attribute!')
        return self.blackboard.UpdateState(self.blackboard_key, update, update_dict_recursive)