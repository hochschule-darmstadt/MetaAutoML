from IAbstractBlackboardAgent import IAbstractBlackboardAgent
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AdapterRuntimeManager import AdapterRuntimeManager
    from Blackboard import Blackboard
    from StrategyController import StrategyController

class AdapterRuntimeManagerAgent(IAbstractBlackboardAgent):
    blackboard_key = 'training_runtime'

    def __init__(self, blackboard: "Blackboard", strategy_controller: "StrategyController", adapter_runtime_manager: "AdapterRuntimeManager"):
        super().__init__(blackboard, strategy_controller, 'training-runtime')
        self.__adapter_runtime_manager = adapter_runtime_manager

    def can_contribute(self) -> bool:
        return self.get_state() != self.__adapter_runtime_manager.get_status_for_blackboard()
        
    def do_contribute(self) -> None:
        session_status = self.__adapter_runtime_manager.get_status_for_blackboard()

        self.update_state(session_status)

        if session_status["status"] != "busy":
            self._log.info(f'Session {self.__adapter_runtime_manager.get_training_id()} is inactive, stopping controller loop.')
            self.unregister()
            raise StopIteration('Training session inactive, stopping..')

        return session_status

    def get_adapter_runtime_manager(self) -> "AdapterRuntimeManager":
        return self.__adapter_runtime_manager