import logging
from rule_engine import Rule
from typing import Callable, Dict
from StrategyController import StrategyController

class IAbstractStrategy():
    """
    Interface representing the functionality any controller strategy must provide.
    """

    def __init__(self, controller: StrategyController) -> None:
        """
        Constructs a new controller strategy.
        ---
        Parameter
        1. controller: The strategy controller to attach to.
        """
        self._log = logging.getLogger(self.__class__.__name__)
        self.controller = controller
        self.rules: Dict[str, set[Rule, Callable]] = {}
        self.register_rules()

    def register_rule(self, name: str, rule: Rule, action: Callable, overwrite_existing: bool = False):
        """
        Indicates whether the blackboard agent wants to contribute something currently.
        ---
        Return a boolean indicating the status
        """
        if name in self.rules and not overwrite_existing:
            raise RuntimeError(f'A rule with the name {name} already exists.')

        self.rules[name] = (rule, action)

        self._log.info(f'Registered rule: {name} ({rule})')

    def register_rules(self):
        """
        Registers all rules relevant to the strategy.
        """
        raise NotImplementedError('Not implemented!')
