import logging
from Blackboard import Blackboard

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
        self.__log = logging.getLogger()
        self.agent_id = agent_id
        self.blackboard = blackboard
        self.blackboard.RegisterAgent(self)
        self.__log.debug(f'Initialized a new blackboard agent: {agent_id}')

    def CanContribute(self) -> bool:
        """
        Indicates whether the blackboard agent wants to contribute something currently
        ---
        Return a boolean indicating the status
        """
        raise RuntimeError('Not implemented!')

    def DoContribute(self) -> any:
        """
        Performs the contribution to the shared blackboard
        """
        raise RuntimeError('Not implemented!')