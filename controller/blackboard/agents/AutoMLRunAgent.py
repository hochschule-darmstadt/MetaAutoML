from managers.adaptermanagers.AutoMLManager import AutoMLManager
from .AbstractAgent import IAbstractBlackboardAgent
from Controller_bgrpc import SessionStatus

class AutoMLRunAgent(IAbstractBlackboardAgent):
    def __init__(self, blackboard, manager: AutoMLManager):
        super().__init__(blackboard, manager.name)
        self.manager = manager

    def CanContribute(self) -> bool:
        return (
            self.blackboard.common_state.get('run_metrics', {}).get(self.agent_id) is None or
            self.manager.get_status().status == SessionStatus.SESSION_STATUS_BUSY
        )
        # FIXME: self.blackboard.common_state.get('phase') == 'running'
        
    def DoContribute(self) -> None:
        automl_status = self.manager.get_status()

        run_metrics = {
            'status': automl_status.status,
            'messages': automl_status.messages,
            'test_score': automl_status.test_score,
            'validation_score': automl_status.validation_score,
            'runtime': automl_status.runtime,
            'prediction_time': automl_status.predictiontime,
            'model': automl_status.model,
            'library': automl_status.library
        }
        
        self.blackboard.common_state.update({
            'run_metrics': self.UpdateNestedState(
                self.blackboard.common_state.get('run_metrics', {}),
                { self.agent_id: run_metrics }
            )
        })

        if automl_status.status != SessionStatus.SESSION_STATUS_BUSY:
            # FIXME: self.__log.info
            print(f'Agent {self.agent_id} is not active: {automl_status.status}')
            # self.Unregister()

        return run_metrics