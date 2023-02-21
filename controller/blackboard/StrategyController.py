import logging, time, json, os
from threading import Timer
from typing import Callable
from datetime import datetime
from DataStorage import DataStorage
from Blackboard import Blackboard
from ThreadLock import ThreadLock
from ControllerBGRPC import *
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from DataAnalysisAgent import DataAnalysisAgent
from AdapterRuntimeManager import AdapterRuntimeManager
from AdapterManagerAgent import AdapterManagerAgent

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class StrategyController(object):
    """
    Strategy controller which supervises the blackboard.
    """,
    def __init__(self, data_storage:DataStorage, request: "CreateTrainingRequest", explainable_lock: ThreadLock, timer_interval: int = 1, multi_fidelity_callback = None, multi_fidelity_level = 0) -> None:
        self._log = logging.getLogger('StrategyController')
        self._log.setLevel(logging.getLevelName(os.getenv("BLACKBOARD_LOGGING_LEVEL")))
        self.__is_running = False
        self.__timer_interval = timer_interval
        self.__timer = None
        self.__update_phase_next_run = None
        self.__blackboard = Blackboard()
        self.__data_storage: DataStorage = data_storage
        self.__request: "CreateTrainingRequest" = request
        self.__explainable_lock = explainable_lock
        #Init training session
        self.__adapter_runtime_manager = AdapterRuntimeManager(self.__data_storage, self.__request, self.__explainable_lock, multi_fidelity_callback = multi_fidelity_callback, multi_fidelity_level = multi_fidelity_level)
        #Init Agents
        for adapter_manager in self.__adapter_runtime_manager.get_adapter_managers():
            AdapterManagerAgent(self.__blackboard, self, adapter_manager)
        AdapterRuntimeManagerAgent(self.__blackboard, self, self.__adapter_runtime_manager)
        DataAnalysisAgent(self.__blackboard, self, self.__adapter_runtime_manager.get_dataset())
        self._log.debug(f'Attached controller to the blackboard, current agents: {len(self.__blackboard.agents)}')

        try:
            session_config = self.__adapter_runtime_manager.get_training_request().configuration
            session_enabled_strategies = session_config.enabled_strategies
            self._log.debug(f'Found {len(session_enabled_strategies)} enabled strategies for the session: {session_enabled_strategies}')
        except Exception as e:
            self._log.error(f'Error while fetching the enabled strategies for the session:')
            self._log.exception(e)
            session_enabled_strategies = []

        self.__blackboard.common_state.update({
            'phase': None,
            'dataset_type': self.__adapter_runtime_manager.get_dataset()['type'],
            'events': [],
            'enabled_strategies': session_enabled_strategies
        })

        self.event_listeners = {}
        self.strategies = []

        from PreprocessingStrategy import PreprocessingStrategyController
        from blackboard.strategies.PreTrainingStrategy import PreTrainingStrategyController
        self.strategies.append(PreprocessingStrategyController(self))
        self.strategies.append(PreTrainingStrategyController(self))
        self.on_event('phase_updated', self.__adapter_runtime_manager.blackboard_phase_update_handler)
        self.set_phase('preprocessing')
        self.start_timer()

    def get_adapter_runtime_manager(self) -> AdapterRuntimeManager:
        """get the __adapter_runtime_manager object of this session

        Returns:
            AdapterRuntimeManager: The __adapter_runtime_manager object
        """
        return self.__adapter_runtime_manager

    def get_explainable_lock(self) -> ThreadLock:
        """get the __explainable_lock object of this session

        Returns:
            ThreadLock: The __explainable_lock object
        """
        return self.__explainable_lock

    def get_data_storage(self) -> DataStorage:
        """get the data_storage object of this session

        Returns:
            DataStorage: The data_storage object
        """
        return self.__data_storage

    def get_request(self) -> "CreateTrainingRequest":
        """get the request object of this session

        Returns:
            "CreateTrainingRequest": The request object
        """
        return self.__request

    def get_training_id(self) -> str:
        """get the training id of this session

        Returns:
            str: The training id which identify this training session
        """
        return self.__adapter_runtime_manager.get_training_id()

    def get_blackboard(self) -> Blackboard:
        return self.__blackboard

    def get_phase(self) -> str:
        return self.__blackboard.get_state('phase')

    def set_phase(self, phase: str, force: bool = False) -> None:
        if force:
            old_phase = self.get_phase()
            self.__blackboard.update_state('phase', phase)
            self.log_event('phase_updated', { 'old_phase': old_phase, 'new_phase': phase })
        else:
            # Update the phase in the next controller loop iteration
            self.__update_phase_next_run = phase

    def wait_for_phase(self, phase: str) -> None:
        while self.get_phase() != phase:
            time.sleep(1)
            self._log.info(f'Waiting for phase: "{phase}" (current: "{self.get_phase()}")')
        self._log.info(f'Waiting finished for phase: {phase}')

    def start_timer(self) -> None:
        if not self.__is_running:
            self.__timer = RepeatTimer(interval=self.__timer_interval, function=self.run_loop)
            self.__timer.daemon = True
            self.__timer.start()
            self._log.debug(f'start_timer: Started controller timer thread: {self.__timer.native_id}')
            self.__is_running = True
            self.set_phase('started', force=True)

    def stop_timer(self) -> None:
        self.__timer.cancel()
        self._log.debug(f'stop_timer: Stopped controller timer thread: {self.__timer.native_id}')
        self.__is_running = False
        self.set_phase('stopped', force=True)

    def run_loop(self) -> None:
        stop_requested = False
        state_changed = False
        if self.__update_phase_next_run is not None:
            self.set_phase(self.__update_phase_next_run, force=True)
            state_changed = True #Phase change changes state
            self.__update_phase_next_run = None
        for agent in list(self.__blackboard.agents.values()):
            if agent.can_contribute():
                self._log.debug(f'run_loop: Executing contribution by agent: {agent.agent_id}')
                try:
                    contribution = agent.do_contribute()
                    state_changed = True
                except StopIteration as err:
                    # An agent requested the controller to stop, will halt after all agents & strategies finished..
                    self._log.error(f'run_loop: Agent "{agent.agent_id}" requested a stop: {err}')
                    stop_requested = True
                except Exception as err:
                    self._log.error(f'run_loop: Could not execute contribution by agent: {agent.agent_id}')
                    self._log.exception(err)
            else:
                self._log.debug(f'run_loop: No contribution by agent: {agent.agent_id}')
        if state_changed:
            self.evaluate_strategy()
        if stop_requested:
            self.stop_timer()

    def is_strategy_enabled(self, strategy_name: str) -> bool:
        return strategy_name in self.__blackboard.get_state('enabled_strategies', [])

    def enable_strategy(self, strategy_name: str) -> None:
        enabled_strategies = self.__blackboard.get_state('enabled_strategies', [])
        if not strategy_name in enabled_strategies:
            enabled_strategies.append(strategy_name)
            self.__blackboard.update_state('enabled_strategies', enabled_strategies)
        self._log.debug(f'enable_strategy: Enabled strategy: {strategy_name}')

    def disable_strategy(self, strategy_name: str) -> None:
        enabled_strategies = self.__blackboard.get_state('enabled_strategies', [])
        if strategy_name in enabled_strategies:
            enabled_strategies.remove(strategy_name)
            self.__blackboard.update_state('enabled_strategies', enabled_strategies)
        self._log.debug(f'disable_strategy: Disabled strategy: {strategy_name}')

    def evaluate_strategy(self) -> None:
        self._log.debug(f'evaluate_strategy: Evaluating strategy based on the new common state..')

        for strategy in self.strategies:
            for rule_name, (rule, action) in strategy.rules.items():
                if self.is_strategy_enabled(rule_name):
                    try:
                        state = self.__blackboard.get_state()
                        if rule.matches(state):
                            try:
                                result = action(state, self.__blackboard, self)
                                self.log_event('strategy_action', { 'rule_name': rule_name, 'result': result })
                            except Exception as err:
                                self._log.error(f'evaluate_strategy: Could not execute strategy action for rule "{rule_name}".')
                                self._log.exception(err)
                    except Exception as err:
                        self._log.error(f'evaluate_strategy: Could not evaluate rule match for rule "{rule_name}".')
                        self._log.exception(err)

    def log_event(self, event_type: str, meta: dict = {}, timestamp: float = None) -> None:
        event = {
            'type': event_type,
            'meta': meta,
            'timestamp': timestamp if timestamp is not None else datetime.now()
        }
        events = self.__blackboard.get_state('events')
        events.append(event)
        self.__blackboard.update_state('events', events)
        self._log.info(f'Encountered event "{event_type}": {meta}')
        for callback in (self.event_listeners.get('*', []) + self.event_listeners.get(event_type, [])):
            self._log.debug(f'Dispatching event callback for "{event_type}": {callback}')
            result = callback(meta, self)
        training_id = self.__adapter_runtime_manager.get_training_id()
        user_id = self.__adapter_runtime_manager.get_user_id()
        if training_id is not None and user_id is not None:
            with self.__data_storage.lock():
                self._log.debug(f'log_event: Updating events in the persistent storage..')
                self.__data_storage.update_training(user_id, training_id, { 'events': events })

    def on_event(self, event_type: str, callback: Callable) -> None:
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = list()
        self.event_listeners[event_type].append(callback)
        self._log.debug(f'on_event: Registered event listener "{event_type}": {callback}')
