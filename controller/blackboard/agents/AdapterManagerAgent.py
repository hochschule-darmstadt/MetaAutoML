from sklearn import metrics
from IAbstractBlackboardAgent import IAbstractBlackboardAgent
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AdapterManager import AdapterManager
    from Blackboard import Blackboard
    from StrategyController import StrategyController

class AdapterManagerAgent(IAbstractBlackboardAgent):
    blackboard_key = 'run_metrics'

    def __init__(self, blackboard: "Blackboard", strategy_controller: "StrategyController", adapter_manager: "AdapterManager"):
        super().__init__(blackboard, strategy_controller, f"training-{adapter_manager.get_training_id()}-adapter-{adapter_manager.get_automl_name()}" )
        self.adapter_manager = adapter_manager

    def can_contribute(self) -> bool:
        return (
            self.get_state({}).get(self.agent_id) is None or
            self.get_state({}).get(self.agent_id) != self.adapter_manager.get_status_for_blackboard()
        )
        
    def do_contribute(self) -> None:
        run_metrics = self.adapter_manager.get_status_for_blackboard()
        self.update_state({ self.agent_id: run_metrics }, True)

        if not self.adapter_manager.is_running():
            self.strategy_controller.log_event('automl_run_finished', { 'name': self.adapter_manager.get_automl_name(), 'run_metrics': run_metrics })
            self._log.info(f'Agent {self.agent_id} is no longer active ({run_metrics["status"]}), unregistering...')
            self.unregister()

        return run_metrics