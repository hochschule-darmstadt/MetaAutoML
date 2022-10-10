from IAbstractBlackboardAgent import IAbstractBlackboardAgent
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Blackboard import Blackboard
    from StrategyController import StrategyController

class DataAnalysisAgent(IAbstractBlackboardAgent):
    blackboard_key = 'dataset_analysis'

    def __init__(self, blackboard: "Blackboard", strategy_controller: "StrategyController", dataset: str):
        super().__init__(blackboard, strategy_controller, 'data-analysis')
        self.__dataset = dataset

    def can_contribute(self) -> bool:
        return (
            self.blackboard.get_state('dataset_analysis') is None and
            self.blackboard.get_state('training_runtime') is not None
        )
    
    def do_contribute(self) -> None:
        dataset_analysis = self.__dataset.get('analysis', {})
        if dataset_analysis is None:
            dataset_analysis = {}
        self.update_state(dataset_analysis)

        # The dataset analysis has to be loaded only once, therefore unregister the agent again
        self.unregister()

        return dataset_analysis