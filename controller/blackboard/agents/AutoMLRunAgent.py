from managers.adaptermanagers.AutoMLManager import AutoMLManager
from .AbstractAgent import IAbstractBlackboardAgent

class AutoMLRunAgent(IAbstractBlackboardAgent):
    def __init__(self, blackboard, manager: AutoMLManager):
        super(blackboard, manager.name)
        self.manager = manager

    def CanContribute(self) -> bool:
        return self.blackboard.common_state.get('phase') == 'running'

    def DoContribute(self) -> None:
        run_metrics = {
            'status': self.manager.__last_status,
            'messages': self.manager.__status_messages,
            'test_score': self.manager.__testScore,
            'validation_score': self.manager.__validationScore,
            'runtime': self.manager.__runtime,
            'prediction_time': self.manager.__predictiontime,
            'model': self.manager.__model,
            'library': self.manager.__library
        }

        self.blackboard.common_state.update({
            'run_metrics': {
                self.manager.name: run_metrics
            }
        })

        return run_metrics