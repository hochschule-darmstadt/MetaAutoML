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


        self._log.info(f'do_finish_pre_training: Finished data preparation, advancing to phase "training"..')
        self.controller.set_phase('training')

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
            self._log.info(f'do_finish_pre_training: Finished data preparation, advancing to phase "training"..')
            self.controller.set_phase('training')
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
            self._log.info(f'do_finish_pre_training: Finished pre training, advancing to phase "training"..')
            controller.set_phase('training')
            controller.disable_strategy('pre_training.finish_pre_training')

    def do_optimum_strategy_callback(self, model_list, _):
        """_summary_

        Args:
            model_list (_type_): _description_
            _ (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Funktion zum Verarbeiten der abgeschlossenen Modelle und Aktualisieren des Blackboards
        blackboard=self.controller.get_blackboard()
        for model in model_list:
            if model.get('status') == 'completed':
                #add_data does not exist in the current version of the Blackboard
                blackboard.add_data({"completed_model": model})
        return model_list

    def do_optimum_strategy(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        """_summary_

        Args:
            state (dict): _description_
            blackboard (Blackboard): _description_
            controller (StrategyController): _description_
        """
        multi_fidelity_dataset_percentage = 0.8
        initial_runtime_limit = controller.get_request().configuration.runtime_limit

        # Setze die globale Multi-Fidelity-Ebene zurück
        self.global_multi_fidelity_level = 1

        # Deaktiviere Multi-Fidelity-Strategie
        controller.disable_strategy('training.optimum_strategy')
        # Starte die erste Iteration
        self.run_iteration(controller, multi_fidelity_dataset_percentage, initial_runtime_limit)
        return

    def run_iteration(self, controller: StrategyController, multi_fidelity_dataset_percentage: float, runtime_limit: int):
        """_summary_

        Args:
            controller (StrategyController): _description_
            multi_fidelity_dataset_percentage (float): _description_
            runtime_limit (int): _description_
        """
        top_model={}
        model_accuracies = {}
        accuracies = []
        consecutive_no_improvement = 0

        while consecutive_no_improvement < 2:
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
            user_id = request.user_id
            training_id = controller.get_training_id()
            dataset_id = request.dataset_id
            model_list = controller.get_data_storage().get_models(user_id,training_id,dataset_id)
            model_count = len(model_list)
            # Wie kann ich die model_list am besten holen hier ?
            completed_models = []
            while model_count!=len(completed_models):
                model_list = controller.get_data_storage().get_models(user_id,training_id,dataset_id)  
                #model.get('status') == ('completed' or "failed") it might not work
                completed_models += [model.get('auto_ml_solution') for model in model_list if model.get('status') in ('completed', 'failed') and model.get('auto_ml_solution') not in completed_models]
                #time.sleep(5)
                
            model_list = controller.get_data_storage().get_models(user_id,training_id,dataset_id)  
            accuracy = [self.get_score(model) for model in model_list]
            print("accuracy: ", accuracy)
            accuracies.append(accuracy)
            #creating key pair value to know which model has which accuracy
            if completed_models not in model_accuracies:
                model_accuracies[completed_models] = []

            model_accuracies[completed_models].append(accuracy)
           # model_accuracies[completed_models] = accuracy
            # Überprüfe, ob eine Verbesserung vorliegt
            epsilon=0.005
            length = len(accuracies)
            if len(accuracies) >= 2: 
                # Loop through each pair of consecutive accuracy arrays starting from the second one
                for i in range(1, len(accuracies)):
                      previous_accuracies = accuracies[i - 1]
                      current_accuracies = accuracies[i]
                      all_smaller_or_equal = True  # Assume they match the condition until proven otherwise
                    # Check corresponding elements in the two lists
                    
                    # Check if each accuracy in the current list is smaller or equal to the previous list's accuracies
                      for j in range(len(current_accuracies)):
                            if current_accuracies[j] >= previous_accuracies[j] + epsilon:
                                all_smaller_or_equal = False
                                consecutive_no_improvement = 0
                                break  # Stop checking as soon as one mismatch is found

                        # Output the result of the comparison for each pair of mini-arrays
                            if all_smaller_or_equal:
                                consecutive_no_improvement += 1
                                print(f"Accuracies at index {i} are all smaller or equal to those at index {i-1} + 0.005")
                            else:
                                print(f"Accuracies at index {i} are NOT all smaller or equal to those at index {i-1} + 0.005")
                else:
                    print("Not enough data to compare accuracies.")
                print("accuracies: ", accuracies)            
            

            # Laufzeit verdoppeln für die nächste Iteration
            runtime_limit *= 2
            
            if consecutive_no_improvement == 2:
                top_model= max(model_accuracies, key=model_accuracies.get)

        self._log.info('Optimum strategy completed.')
        controller.set_phase('completed')
