import logging
from ..Controller import StrategyController

logger = logging.getLogger('strategy')

def check_conditions(condition: bool, log_enabled: str = None, log_disabled: str = None, *args):
    def enabled_strategy_action(func):
        if log_enabled is not None:
            logger.info(log_enabled)
        def wrapped_strategy_action(c):
            return func(c, *args)
        return wrapped_strategy_action

    def disabled_strategy_action(func):
        if log_disabled is not None:
            logger.info(log_disabled)
        def noop_strategy_action(c):
            return
        return noop_strategy_action

    return enabled_strategy_action if condition else disabled_strategy_action

def check_strategy_enabled(controller: StrategyController, name: str):
    return check_conditions(
        name in controller.blackboard.common_state.get('enabled_strategies', []),
        f'Strategy "{name}" has been activated.',
        f'Strategy "{name}" has been deactivated.',
        controller
    )