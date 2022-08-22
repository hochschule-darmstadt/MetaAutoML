from managers.adaptermanagers.AutoMLManager import AutoMLManager
from .AbstractAgent import IAbstractBlackboardAgent
from Controller_bgrpc import SessionStatus

class AutoMLRunAgent(IAbstractBlackboardAgent):
    blackboard_key = 'run_metrics'

    def __init__(self, blackboard, controller, manager: AutoMLManager):
        super().__init__(blackboard, controller, manager.name)
        self.manager = manager

    def CanContribute(self) -> bool:
        return (
            self.GetState({}).get(self.agent_id) is None or
            self.GetState({}).get(self.agent_id) != self.manager.get_status().to_dict()
        )
        
    def DoContribute(self) -> None:
        automl_status = self.manager.get_status()

        run_metrics = {
            'status': automl_status.status,
            # 'messages': automl_status.messages,
            'test_score': automl_status.test_score,
            'validation_score': automl_status.validation_score,
            'runtime': automl_status.runtime,
            'prediction_time': automl_status.predictiontime,
            'model': automl_status.model,
            'library': automl_status.library
        }
        
        self.UpdateState({ self.agent_id: run_metrics }, True)

        if not self.manager.is_running():
            self.controller.LogEvent('automl_run_finished', { 'name': self.manager.name, 'run_metrics': run_metrics })
            self._log.info(f'Agent {self.agent_id} is no longer active ({automl_status.status}), unregistering...')
            self.Unregister()

        return run_metrics