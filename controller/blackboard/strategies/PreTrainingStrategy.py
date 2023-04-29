import json, time
from rule_engine import Rule, Context, DataType, type_resolver_from_dict
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from ControllerBGRPC import DataType as GrpcDataType
from IAbstractStrategy import IAbstractStrategy
from StrategyController import StrategyController
from Blackboard import Blackboard

class PreTrainingStrategyController(IAbstractStrategy):
    global_multi_fidelity_level = 1

    def register_rules(self):
        training_context = Context(
            type_resolver=type_resolver_from_dict({
                'phase': DataType.STRING,
                'dataset_type' : DataType.STRING,
                'enabled_strategies': DataType.ARRAY(DataType.STRING, value_type_nullable=False),
                'dataset_analysis': DataType.MAPPING(
                    key_type=DataType.STRING,
                    value_type=DataType.UNDEFINED
                ),
                'training_runtime': DataType.MAPPING(
                    key_type=DataType.STRING,
                    value_type=DataType.UNDEFINED
                )
            })
        )

        self.register_rule(
            'pre_training.top_3_models',
            Rule("phase == 'pre_training'", context=training_context),
            self.do_top_3_models
        )

        self.register_rule(
            'pre_training.multi_fidelity',
            Rule("phase == 'pre_training'", context=training_context),
            self.do_multi_fidelity
        )

        self.register_rule(
            'pre_training.finish_pre_training',
            Rule("""
                phase == 'pre_training' and
                ('pre_training.top_3_models' not in enabled_strategies) and
                ('pre_training.multi_fidelity' not in enabled_strategies)
            """, context=training_context),
            self.do_finish_pre_training
        )

        # Force enable this strategy to ensure pre training always finishes
        self.controller.enable_strategy('pre_training.finish_pre_training')

    def get_score(self, model):
        if model.get('test_score').get(':accuracy') is not None:
            return model.get('test_score').get(':accuracy')
        else:
            return 0.0

    def do_top_3_models_callback(self, model_list):
        model_list.sort(key=lambda model: self.get_score(model), reverse=True)

        relevant_auto_ml_solutions = []
        for model in model_list[0:3]:
            #Only add max 3 Adapters
            if model.get('status') == 'completed':
                relevant_auto_ml_solutions.append(model.get('auto_ml_solution'))

        relevant_auto_ml_solutions = list(set(relevant_auto_ml_solutions))
        self.controller.get_adapter_runtime_manager().update_adapter_manager_list(relevant_auto_ml_solutions)


        self._log.info(f'do_finish_pre_training: Finished data preparation, advancing to phase "running"..')
        self.controller.set_phase('running')

        return

    def do_top_3_models(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        if self.global_multi_fidelity_level == 1:
            self.global_multi_fidelity_level = 0
        #disable Multi-Fidelity-Strategy
        controller.disable_strategy('pre_training.top_3_models')

        #start new training
        strategy_controller = StrategyController(controller.get_data_storage(), controller.get_request(), controller.get_explainable_lock(), multi_fidelity_callback=self.do_top_3_models_callback, multi_fidelity_level=1)
        return
    
    def do_multi_fidelity_callback(self, model_list):
        model_list.sort(key=lambda model: model.get('test_score'), reverse=True)

        relevant_auto_ml_solutions = []
        for model in model_list[0:3]:
            #Only add max 3 Adapters
            if model.get('status') == 'completed':
                relevant_auto_ml_solutions.append(model.get('auto_ml_solution'))

        relevant_auto_ml_solutions = list(set(relevant_auto_ml_solutions))
        self.controller.get_adapter_runtime_manager().update_adapter_manager_list(relevant_auto_ml_solutions)


        self._log.info(f'do_finish_pre_training: Finished data preparation, advancing to phase "running"..')
        self.controller.set_phase('running')

        return

    def do_multi_fidelity(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        if self.global_multi_fidelity_level == 1:
            self.global_multi_fidelity_level = 0
        #disable Multi-Fidelity-Strategy
        controller.disable_strategy('pre_training.multi_fidelity')

        #start new training
        strategy_controller = StrategyController(controller.get_data_storage(), controller.get_request(), controller.get_explainable_lock(), multi_fidelity_callback=self.do_multi_fidelity_callback, multi_fidelity_level=1)
        return

    def do_finish_pre_training(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        if self.global_multi_fidelity_level != 0:
            self._log.info(f'do_finish_pre_training: Finished pre training, advancing to phase "running"..')
            controller.set_phase('running')
            controller.disable_strategy('pre_training.finish_pre_training')

