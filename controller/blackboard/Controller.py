import logging, time
from threading import Thread, Lock
from .Blackboard import Blackboard

class StrategyController(object):
    """
    Strategy controller which supervises the blackboard.
    """

    def __init__(self, blackboard: Blackboard) -> None:
        self._log = logging.getLogger('strategy-controller')
        self._log.setLevel(logging.DEBUG) # FIXME: Remove this line, only for debugging
        self.blackboard = blackboard
        self._log.debug(f'Attached controller to the blackboard, current agents: {len(self.blackboard.agents)}')

        self.blackboard.common_state.update({
            'phase': 'initialization',
            'events': [],
            'enabled_strategies': [
                # FIXME: Inherit from session configuration
                'data_preparation.ignore_redundant_features',
                'data_preparation.ignore_redundant_samples',
                'data_preparation.split_large_datasets',
                'data_preparation.finish_preprocessing',
            ]
        })

        self.strategies = []

        from blackboard.strategies.DataPreparationStrategy import DataPreparationStrategyController
        self.strategies.append(DataPreparationStrategyController(self))

    def GetPhase(self) -> str:
        return self.blackboard.GetState('phase')

    def SetPhase(self, phase) -> None:
        old_phase = self.GetPhase()
        self.blackboard.UpdateState('phase', phase)
        self.LogEvent('phase_updated', { 'old_phase': old_phase, 'new_phase': phase })

    def WaitForPhase(self, phase) -> None:
        while self.GetPhase() != phase:
            time.sleep(2) # FIXME: Remove (for testing purposes)
            self._log.info(f'Waiting for phase: "{phase}" (current: "{self.GetPhase()}")')
        self._log.info(f'Waiting finished for phase: {phase}')
      
    def StartLoop(self) -> None:
        self.__is_running = True
        self.__lock = Lock()
        self.__thread = Thread(target=self.RunLoop)
        self.__thread.daemon = True
        self.__thread.start()
        self._log.debug(f'Started controller thread: {self.__thread.native_id}')

    def RunLoop(self) -> None:
        while self.__is_running:
            time.sleep(2) # FIXME: Remove (for testing purposes)
            self.__lock.acquire()
            stop_requested = False
            state_changed = False
            for agent in list(self.blackboard.agents.values()):
                if agent.CanContribute():
                    self._log.debug(f'Executing contribution by agent: {agent.agent_id}')
                    try:
                        contribution = agent.DoContribute()
                        state_changed = True
                    except StopIteration as err:
                        # An agent requested the controller to stop, will halt after all agents & strategies finished..
                        self._log.error(f'Agent "{agent.agent_id}" requested a stop: {err}')
                        stop_requested = True
                    except Exception as err:
                        self._log.error(f'Could not execute contribution by agent: {agent.agent_id}')
                        self._log.exception(err)
                else:
                    self._log.debug(f'No contribution by agent: {agent.agent_id}')
            if state_changed:
                # FIXME: Remove (for testing purposes)
                import json
                self._log.info('Current common_state:\n'+json.dumps(self.blackboard.common_state, indent=2))
                self.EvaluateStrategy()
            self.__lock.release()
            if stop_requested:
                self.StopLoop()

    def StopLoop(self) -> None:
        self.__lock.acquire()
        self.__is_running = False
        self._log.debug(f'Stopped controller thread: {self.__thread.native_id}')
        self.__lock.release()

    def IsStrategyEnabled(self, strategy_name: str) -> bool:
        return strategy_name in self.blackboard.GetState('enabled_strategies', [])

    def EnableStrategy(self, strategy_name: str):
        enabled_strategies = self.blackboard.GetState('enabled_strategies', [])
        if not strategy_name in enabled_strategies:
            enabled_strategies.append(strategy_name)
            self.blackboard.UpdateState('enabled_strategies', enabled_strategies)
        self._log.debug(f'Enabled strategy: {strategy_name}')

    def DisableStrategy(self, strategy_name: str):
        enabled_strategies = self.blackboard.GetState('enabled_strategies', [])
        if strategy_name in enabled_strategies:
            enabled_strategies.remove(strategy_name)
            self.blackboard.UpdateState('enabled_strategies', enabled_strategies)
        self._log.debug(f'Disabled strategy: {strategy_name}')

    def EvaluateStrategy(self) -> None:
        self._log.debug(f'Evaluating strategy based on the new common state..')

        for strategy in self.strategies:
            for rule_name, (rule, action) in strategy.rules.items():
                if self.IsStrategyEnabled(rule_name):
                    try:
                        if rule.matches(self.blackboard.common_state):
                            try:
                                result = action(self.blackboard.common_state, self.blackboard, self)
                                self.LogEvent('strategy_action', { 'rule_name': rule_name, 'result': result })
                            except Exception as err:
                                self._log.error(f'Could not execute strategy action for rule "{rule_name}".')
                                self._log.exception(err)
                    except Exception as err:
                        self._log.error(f'Could not evaluate rule match for rule "{rule_name}".')
                        self._log.exception(err)

    def LogEvent(self, event_type: str, meta: dict = {}):
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'meta': meta
        }
        self.blackboard.common_state['events'].append(event)
        self._log.info(f'Encountered event "{event_type}": {meta}')