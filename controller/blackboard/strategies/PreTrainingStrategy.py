import json, time
import math
from rule_engine import Rule, Context, DataType, type_resolver_from_dict
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from ControllerBGRPC import DataType as GrpcDataType
from IAbstractStrategy import IAbstractStrategy
from StrategyController import StrategyController
from Blackboard import Blackboard
import copy

class PreTrainingStrategyController(IAbstractStrategy):
    global_multi_fidelity_level = 1
    total_runtime_limit = 0
    sum_dataset_all = 0

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
            'training.optimum_strategy',
            Rule("phase == 'training'", context=training_context),
            self.do_optimum_strategy
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

    def do_top_3_models_callback(self, model_list, _):
        multi_fidelity_dataset_percentage = 0.1
        model_list.sort(key=lambda model: self.get_score(model), reverse=True)

        self.controller.get_request().configuration.runtime_limit = self.controller.get_request().configuration.runtime_limit - int(self.controller.get_request().configuration.runtime_limit * multi_fidelity_dataset_percentage)

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
        multi_fidelity_dataset_percentage = 0.1
        if self.global_multi_fidelity_level == 1:
            self.global_multi_fidelity_level = 0
        #disable Multi-Fidelity-Strategy
        controller.disable_strategy('pre_training.top_3_models')
        request = self.controller.get_request()
        request_copy = copy.deepcopy(request)
        request_copy.configuration.runtime_limit = int(request_copy.configuration.runtime_limit * multi_fidelity_dataset_percentage)
        #start new training
        strategy_controller = StrategyController(controller.get_data_storage(), request_copy, controller.get_explainable_lock(), multi_fidelity_callback=self.do_top_3_models_callback, multi_fidelity_level=multi_fidelity_dataset_percentage)
        return

    def do_multi_fidelity_callback(self, model_list, old_multi_fidelity_level):
        model_list.sort(key=lambda model: self.get_score(model), reverse=True)

        completed_model_list = []
        for model in model_list:
            if model.get('status') == 'completed':
                completed_model_list.append(model)

        relevant_auto_ml_solutions = []
        for model in completed_model_list[0:max(int(len(completed_model_list)/2), 1)]:
            #Only add max half of all adapters
            if model.get('status') == 'completed':
                relevant_auto_ml_solutions.append(model.get('auto_ml_solution'))

        relevant_auto_ml_solutions = list(set(relevant_auto_ml_solutions))
        self.controller.get_adapter_runtime_manager().update_adapter_manager_list(relevant_auto_ml_solutions)

        if len(relevant_auto_ml_solutions) <= 1:
            configuration = self.controller.get_request().configuration
            new_dataset_size = old_multi_fidelity_level*2
            not_used_runtime = 0
            while len(relevant_auto_ml_solutions) < (1 / new_dataset_size):
                not_used_runtime += int(self.total_runtime_limit * (new_dataset_size / self.sum_dataset_all))
                new_dataset_size *= 2
            configuration.runtime_limit = int(self.total_runtime_limit * (new_dataset_size / self.sum_dataset_all)) + not_used_runtime
            request = self.controller.get_request()
            request.configuration = configuration
            self._log.info(f'do_finish_pre_training: Finished data preparation, advancing to phase "running"..')
            self.controller.set_phase('running')
        else:
            #adjust request object for multi fidelity
            configuration = self.controller.get_request().configuration
            configuration.selected_auto_ml_solutions = relevant_auto_ml_solutions
            new_dataset_size = old_multi_fidelity_level*2
            not_used_runtime = 0
            while len(relevant_auto_ml_solutions) < (1 / new_dataset_size):
                not_used_runtime += int(self.total_runtime_limit * (new_dataset_size / self.sum_dataset_all))
                new_dataset_size *= 2
            configuration.runtime_limit = int(self.total_runtime_limit * (new_dataset_size / self.sum_dataset_all)) + not_used_runtime
            request = self.controller.get_request()
            request.configuration = configuration

            strategy_controller = StrategyController(self.controller.get_data_storage(), request, self.controller.get_explainable_lock(), multi_fidelity_callback=self.do_multi_fidelity_callback, multi_fidelity_level=new_dataset_size)

        return

    def do_multi_fidelity(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        if self.global_multi_fidelity_level == 1:
            self.global_multi_fidelity_level = 0
        #disable Multi-Fidelity-Strategy
        controller.disable_strategy('pre_training.multi_fidelity')

        configuration = self.controller.get_request().configuration
        amount_ml_solutions = len(configuration.selected_auto_ml_solutions)

        self.total_runtime_limit = configuration.runtime_limit
        amount_iterations = int(math.log(amount_ml_solutions, 2))
        dataset_size_begin = 0.5**amount_iterations
        for i in range(0, amount_iterations+1):
            self.sum_dataset_all += 0.5**i

        #adjust time limit for first training
        configuration.runtime_limit = int(self.total_runtime_limit * (dataset_size_begin / self.sum_dataset_all))
        request = self.controller.get_request()
        request.configuration = configuration

        #start new training
        strategy_controller = StrategyController(controller.get_data_storage(), controller.get_request(), controller.get_explainable_lock(), multi_fidelity_callback=self.do_multi_fidelity_callback, multi_fidelity_level=dataset_size_begin)
        return

    def do_finish_pre_training(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        if self.global_multi_fidelity_level != 0:
            self._log.info(f'do_finish_pre_training: Finished pre training, advancing to phase "running"..')
            controller.set_phase('running')
            controller.disable_strategy('pre_training.finish_pre_training')

    def do_optimum_strategy_callback(self, model_list, _):
        # Funktion zum Verarbeiten der abgeschlossenen Modelle und Aktualisieren des Blackboards
        for model in model_list:
            if model.get('status') == 'completed':
                self.blackboard.add_data({"completed_model": model})
        return model_list

    def do_optimum_strategy(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        multi_fidelity_dataset_percentage = 0.8
        initial_runtime_limit = controller.get_request().configuration.runtime_limit

        # Setze die globale Multi-Fidelity-Ebene zurück
        self.global_multi_fidelity_level = 1

        # Deaktiviere Multi-Fidelity-Strategie
        controller.disable_strategy('pre_training.optimum_strategy')

        # Starte die erste Iteration
        self.run_iteration(controller, multi_fidelity_dataset_percentage, initial_runtime_limit)
        return

    def run_iteration(self, controller: StrategyController, multi_fidelity_dataset_percentage: float, runtime_limit: int):
        accuracies = []
        consecutive_no_improvement = 0

        while consecutive_no_improvement < 3:
            # Neue Trainingsdurchlaufkonfiguration definieren
            request = controller.get_request()
            request_copy = copy.deepcopy(request)
            request_copy.configuration.runtime_limit = runtime_limit
            request_copy.configuration.dataset_percentage = multi_fidelity_dataset_percentage

            # Starte neuen Trainingsdurchlauf
            strategy_controller = StrategyController(
                controller.get_data_storage(), request_copy, controller.get_explainable_lock(),
                multi_fidelity_callback=self.do_optimum_strategy_callback,
                multi_fidelity_level=multi_fidelity_dataset_percentage
            )

            # Warte auf den Abschluss des Trainings und erhalte die Modelle
            # TO-DO
            # user_id von dem training
            user_id = controller.get_request()['user_id']
            training_id = controller.get_training_id()
            dataset_id = controller.get_request()['dataset_id']
            model_list = controller.get_data_storage().get_models(user_id,training_id,dataset_id)
            # Wie kann ich die model_list am besten holen hier ?
            completed_models = [model for model in model_list if model.get('status') == 'completed']
            if not completed_models:
                break

            # Berechne die Genauigkeit
            accuracy = max(self.get_score(model) for model in completed_models)
            accuracies.append(accuracy)

            # Überprüfe, ob eine Verbesserung vorliegt
            if len(accuracies) > 1 and accuracies[-1] <= accuracies[-2]:
                consecutive_no_improvement += 1
            else:
                consecutive_no_improvement = 0

            # Laufzeit verdoppeln für die nächste Iteration
            runtime_limit *= 2

        self._log.info('Optimum strategy completed.')
        controller.set_phase('completed')
