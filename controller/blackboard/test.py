# FIXME: Remove file! (for testing/debugging only)

import logging, time, random
from Blackboard import Blackboard
from Controller import StrategyController
from agents.AbstractAgent import IAbstractBlackboardAgent
from agents.DataAnalysisAgent import DataAnalysisAgent

class DummyAgent(IAbstractBlackboardAgent):
    def CanContribute(self) -> bool:
        return random.randint(0, 1) == 1
    
    def DoContribute(self) -> None:
        self.blackboard.common_state.update({
            self.agent_id: {
                'test': random.randint(3, 6)
            }
        })

logging.basicConfig(level=logging.DEBUG)

blackboard = Blackboard()

dummy_agent1 = DummyAgent(blackboard=blackboard, agent_id='agent1')

controller = StrategyController(blackboard)
controller.StartLoop()
time.sleep(5)
controller.SetPhase('data_preparation')
dataset_analysis_agent = DataAnalysisAgent(blackboard=blackboard, agent_id='dataset_analysis')
time.sleep(60)
controller.StopLoop()

print(blackboard.ExportCommonState())