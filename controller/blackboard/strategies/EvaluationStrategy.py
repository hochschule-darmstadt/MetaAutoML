import json
import time
import math
from rule_engine import Rule, Context, DataType, type_resolver_from_dict
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from ControllerBGRPC import DataType as GrpcDataType
from IAbstractStrategy import IAbstractStrategy
from StrategyController import StrategyController
from Blackboard import Blackboard
import copy

class EvaluationStrategy(IAbstractStrategy):
    global_multi_fidelity_level = 1
    total_runtime_limit = 0
    sum_dataset_all = 0

    def register_rules(self):
        """
        Registers the rules for the training strategy.

        This method sets up the context for the rules and registers the rules
        for the `training.optimum_strategy` and `training.finish_training` actions.
        It also forces the enabling of the `training.finish_training` strategy.
        """
        training_context = Context(
            type_resolver=type_resolver_from_dict({
                'phase': DataType.STRING,
                'dataset_type': DataType.STRING,
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
            'evaluation.optimum_strategy',
            Rule("phase == 'evaluation'", context=training_context),
            self.do_optimum_strategy
        )
        self.register_rule(
            'evaluation.finish_training',
            Rule("""
                phase == 'evaluation' and
                ('evaluation.optimum_strategy' not in enabled_strategies)
            """, context=training_context),
            self.do_finish_training
        )
        # Force enable this strategy to ensure training always finishes
        self.controller.enable_strategy('evaluation.finish_training')

    def get_score(self, model):
        """
        Retrieves the accuracy score of a given model.

        Args:
            model (dict): The model for which the score is to be retrieved.

        Returns:
            float: The accuracy score of the model. If no accuracy score is found, returns 0.0.
        """
        if model.get('test_score') and model.get('test_score').get(':accuracy') is not None:
            return model.get('test_score').get(':accuracy')
        else:
            return 0.0

    def do_optimum_strategy_callback(self, model_list, controller: StrategyController):
        """
        Callback function for handling completed models in the optimum strategy.

        Args:
            model_list (list): List of models.
            controller (StrategyController): The strategy controller instance.

        Returns:
            list: The updated model list.
        """
        blackboard = controller.get_blackboard()
        for model in model_list:
            if model.get('status') == 'completed':
                print(f"Completed Model:{model}")
                #blackboard.setadd_data({"completed_model": model})
        return model_list

    def do_optimum_strategy(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        """
        Executes the optimum strategy.

        Args:
            state (dict): The current state.
            blackboard (Blackboard): The blackboard instance.
            controller (StrategyController): The strategy controller instance.
        """
        self._log.info("Starting optimum strategy")
        multi_fidelity_dataset_percentage = 0.8
        initial_runtime_limit = controller.get_request().configuration.runtime_limit

        self.global_multi_fidelity_level = 1

        controller.disable_strategy('evaluation.optimum_strategy')

        self.run_iteration(controller, multi_fidelity_dataset_percentage, initial_runtime_limit)

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

    def do_finish_training(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        """
        Finishes the training phase and advances to the next phase.

        Args:
            state (dict): The current state.
            blackboard (Blackboard): The blackboard instance.
            controller (StrategyController): The strategy controller instance.
        """
        if self.global_multi_fidelity_level != 0:
            self._log.info('Finished training, advancing to phase "evaluation"')
            controller.set_phase('evaluation')
            controller.disable_strategy('evaluation.finish_training')
