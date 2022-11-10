import json, time
from rule_engine import Rule, Context, DataType, type_resolver_from_dict
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from ControllerBGRPC import DataType as GrpcDataType
from IAbstractStrategy import IAbstractStrategy
from StrategyController import StrategyController
from Blackboard import Blackboard

class PreTrainingStrategyController(IAbstractStrategy):
    def register_rules(self):
        pretraining_context = Context(
            type_resolver=type_resolver_from_dict({
                'phase': DataType.STRING,
                'dataset_type' : DataType.STRING,
                'enabled_strategies': DataType.ARRAY(DataType.STRING, value_type_nullable=False),
                'dataset_analysis': DataType.MAPPING(
                    key_type=DataType.STRING,
                    value_type=DataType.UNDEFINED
                )
            })
        )

        self.register_rule(
            'pretraining.multi_fidelity_optimization',
            Rule("phase == 'pretraining'", context=pretraining_context),
            self.do_multi_findelity_opimization
        )

        self.register_rule(
            'pretraining.finish_pretraining',
            Rule("phase == 'pretraining'", context=pretraining_context),
            self.do_finish_pretraining
        )

        # Force enable this strategy to ensure preprocessing always finishes
        self.controller.enable_strategy('pretraining.finish_pretraining')

    def do_multi_findelity_opimization(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        controller.disable_strategy('pretraining.multi_fidelity_optimization')

    def do_finish_pretraining(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        self._log.info(f'do_finish_pretraining: Finished pretraining, advancing to phase "running"..')
        controller.set_phase('running')
        controller.disable_strategy('pretraining.finish_pretraining')