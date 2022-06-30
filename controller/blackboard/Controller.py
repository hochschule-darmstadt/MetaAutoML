import logging, time
from durable.lang import post
from durable.engine import MessageNotHandledException, MessageObservedException
from threading import Thread
from .Blackboard import Blackboard

class StrategyController(object):
    """
    Strategy controller which supervises the blackboard.
    """

    def __init__(self, blackboard: Blackboard) -> None:
        self.__log = logging.getLogger('strategy-controller')
        self.blackboard = blackboard
        self.__log.debug(f'Attached controller to the blackboard, current agents: {len(self.blackboard.agents)}')

        self.blackboard.common_state.update({
            'phase': 'initialization',
            'enabled_strategies': [
                'data_preparation.split_large_datasets',
                'data_preparation.omit_empty_columns'
            ]
        })

        self.strategies = []

        from blackboard.strategies.DataPreparationStrategy import DataPreparationStrategyController
        self.strategies.append(DataPreparationStrategyController(self))

    def GetPhase(self) -> str:
        return self.blackboard.common_state.get('phase')

    def SetPhase(self, phase) -> None:
        self.blackboard.common_state.update({ 'phase': phase })
        
    def StartLoop(self) -> None:
        self.__is_running = True
        self.__thread = Thread(target=self.RunLoop)
        self.__thread.daemon = True
        self.__thread.start()
        self.__log.debug(f'Started controller thread: {self.__thread.native_id}')

    def RunLoop(self) -> None:
        while self.__is_running:
            time.sleep(2) # FIXME: Remove (for testing purposes)
            state_changed = False
            for agent in self.blackboard.agents.values():
                if agent.CanContribute():
                    self.__log.debug(f'Executing contribution by agent: {agent.agent_id}')
                    contribution = agent.DoContribute()
                    # TODO: post(agent.agent_id, contribution)
                    state_changed = True
                    self.__log.info(self.blackboard.common_state)
                else:
                    self.__log.debug(f'No contribution by agent: {agent.agent_id}')
            if state_changed:
                self.EvaluateStrategy()

    def StopLoop(self) -> None:
        self.__is_running = False
        self.__log.debug(f'Stopped controller thread: {self.__thread.native_id}')

    def EvaluateStrategy(self) -> None:
        self.__log.info(f'Evaluating strategy based on the new common state..')

        try:
            # FIXME: The event names have to be unique (per session!) otherwise this does not work
            post('state_update', self.blackboard.common_state)
        except MessageObservedException as e:
            self.__log.debug('Blackboard state already observed in the previous run: ', e)
        except MessageNotHandledException as e:
            # FIXME: self.__log.debug('Blackboard state change didnt cause any actions: ', e)
            pass