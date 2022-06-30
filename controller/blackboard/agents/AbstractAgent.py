import logging, collections.abc
from ..Blackboard import Blackboard

class IAbstractBlackboardAgent():
    """
    Interface representing the functionality any blackboard agent must provide
    """

    def __init__(self, blackboard: Blackboard, agent_id: str) -> None:
        """
        Constructs a new blackboard agent
        ---
        Parameter
        1. blackboard: The blackboard to attach to
        """
        self.agent_id = agent_id
        self.__log = logging.getLogger(self.agent_id)
        self.__log.debug(f'Initialized blackboard agent: "{self.agent_id}"')
        self.blackboard = blackboard
        self.blackboard.RegisterAgent(self)

    def CanContribute(self) -> bool:
        """
        Indicates whether the blackboard agent wants to contribute something currently.
        ---
        Return a boolean indicating the status
        """
        raise RuntimeError('Not implemented!')

    def DoContribute(self) -> any:
        """
        Performs the contribution to the shared blackboard.
        """
        raise RuntimeError('Not implemented!')

    def Unregister(self):
        """
        Unregisters the agent itself from the blackboard.
        """
        self.blackboard.UnregisterAgent(self)

    def UpdateNestedState(self, d, u) -> dict:
        """
        Performs a deep (recursive) update on the common state and returns the new state dict.
        """
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = self.UpdateNestedState(d.get(k, {}), v)
            else:
                d[k] = v
        return d