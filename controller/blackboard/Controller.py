import logging, time
from threading import Timer, Lock
from typing import Callable
from datetime import datetime
from persistence.data_storage import DataStorage
from .Blackboard import Blackboard

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class StrategyController(object):
    """
    Strategy controller which supervises the blackboard.
    """

    def __init__(self, blackboard: Blackboard, data_storage: DataStorage, timer_interval: int = 1) -> None:
        self._log = logging.getLogger('strategy-controller')
        self._log.setLevel(logging.DEBUG) # FIXME: Remove this line, only for debugging
        self.__is_running = False
        self.__timer_interval = timer_interval
        self.__timer = None
        self.blackboard = blackboard
        self.data_storage = data_storage
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

        self.event_listeners = {}
        self.strategies = []

        from blackboard.strategies.DataPreparationStrategy import DataPreparationStrategyController
        self.strategies.append(DataPreparationStrategyController(self))

    def GetPhase(self) -> str:
        return self.blackboard.GetState('phase')

    def SetPhase(self, phase: str) -> None:
        old_phase = self.GetPhase()
        self.blackboard.UpdateState('phase', phase)
        self.LogEvent('phase_updated', { 'old_phase': old_phase, 'new_phase': phase })

    def WaitForPhase(self, phase: str) -> None:
        while self.GetPhase() != phase:
            time.sleep(1)
            self._log.info(f'Waiting for phase: "{phase}" (current: "{self.GetPhase()}")')
        self._log.info(f'Waiting finished for phase: {phase}')
      
    def StartTimer(self) -> None:
        if not self.__is_running:
            self.__lock = Lock()
            self.__timer = RepeatTimer(interval=self.__timer_interval, function=self.RunLoop)
            self.__timer.daemon = True
            self.__timer.start()
            self._log.debug(f'Started controller timer thread: {self.__timer.native_id}')
            self.__is_running = True

    def StopTimer(self) -> None:
        self.__lock.acquire()
        self.__timer.cancel()
        self._log.debug(f'Stopped controller timer thread: {self.__timer.native_id}')
        self.__is_running = False
        self.__lock.release()

        # FIXME: Remove (for testing purposes)
        import json
        self._log.info('Final common_state:\n'+json.dumps(self.blackboard.common_state, indent=2, default=str))

    def RunLoop(self) -> None:
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
            self.EvaluateStrategy()
        self.__lock.release()
        if stop_requested:
            self.StopTimer()

    def IsStrategyEnabled(self, strategy_name: str) -> bool:
        return strategy_name in self.blackboard.GetState('enabled_strategies', [])

    def EnableStrategy(self, strategy_name: str) -> None:
        enabled_strategies = self.blackboard.GetState('enabled_strategies', [])
        if not strategy_name in enabled_strategies:
            enabled_strategies.append(strategy_name)
            self.blackboard.UpdateState('enabled_strategies', enabled_strategies)
        self._log.debug(f'Enabled strategy: {strategy_name}')

    def DisableStrategy(self, strategy_name: str) -> None:
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
                                action_started = datetime.now()
                                result = action(self.blackboard.common_state, self.blackboard, self)
                                self.LogEvent('strategy_action', { 'rule_name': rule_name, 'result': result })
                            except Exception as err:
                                self._log.error(f'Could not execute strategy action for rule "{rule_name}".')
                                self._log.exception(err)
                    except Exception as err:
                        self._log.error(f'Could not evaluate rule match for rule "{rule_name}".')
                        self._log.exception(err)

    def LogEvent(self, event_type: str, meta: dict = {}, timestamp: float = None) -> None:
        event = {
            'type': event_type,
            'meta': meta,
            'timestamp': timestamp if timestamp is not None else datetime.now()
        }
        self.blackboard.common_state['events'].append(event)
        self._log.info(f'Encountered event "{event_type}": {meta}')
        for callback in (self.event_listeners.get('*', []) + self.event_listeners.get(event_type, [])):
            self._log.debug(f'Dispatching event callback for "{event_type}": {callback}')
            result = callback(meta, self)
        session_id = self.blackboard.GetState('session', {}).get('id')
        session_username = self.blackboard.GetState('session', {}).get('configuration', {}).get('username')
        if session_id and session_username:
            self._log.debug(f'Updating events in the persistent storage..')
            self.data_storage.UpdateTraining(session_username, session_id, { 'events': self.blackboard.GetState('events', []) })

    def OnEvent(self, event_type: str, callback: Callable) -> None:
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = list()
        self.event_listeners[event_type].append(callback)
        self._log.debug(f'Registered event listener "{event_type}": {callback}')