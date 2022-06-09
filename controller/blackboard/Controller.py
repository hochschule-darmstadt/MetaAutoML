import logging, time
from durable.lang import post
from durable.engine import MessageNotHandledException, MessageObservedException
from threading import Thread
from Blackboard import Blackboard
from strategies.DataPreparationStrategy import DataPreparationStrategyController

class StrategyController(object):
    """
    Strategy controller which supervises the blackboard.
    """

    def __init__(self, blackboard: Blackboard) -> None:
        self.__log = logging.getLogger()
        self.blackboard = blackboard
        self.__log.debug(f'Attached controller to the blackboard, current agents: {len(self.blackboard.agents)}')

        self.blackboard.common_state.update({
            'phase': 'initialization',
            'enabled_strategies': [
                # TODO: Implement (via decorators on rules?)
                # def check_enabled_strategy(strategy):
                #   def inner(func):
                #     # if(strategy == 'test'):
                #     def wrapper(*args, **kwargs):
                #         func(*args, **kwargs)
                #     return wrapper
                #   return inner
                #
                # @check_enabled_strategy('data_preparation.split_large_datasets')

                'data_preparation.split_large_datasets',
                'data_preparation.omit_empty_columns'
            ]
        })

        self.strategies = []
        self.strategies.append(DataPreparationStrategyController())

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
            for agent in self.blackboard.agents:
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
            post('state_update', self.blackboard.common_state)
        except MessageObservedException as e:
            self.__log.debug('Blackboard state already observed in the previous run: ', e)
        except MessageNotHandledException as e:
            # FIXME: self.__log.debug('Blackboard state change didnt cause any actions: ', e)
            pass