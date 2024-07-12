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
from DataStorage import DataStorage 

class EvaluationStrategy(IAbstractStrategy):
    global_multi_fidelity_level = 1

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
        for model in model_list:
            if model.get('status') == 'completed':
                print(f"Completed Model:{model}")      
        self._log.info('Optimum strategy completed.')
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
      
        initial_runtime_limit = controller.get_request().configuration.runtime_limit
        
        self.global_multi_fidelity_level = 1
        multi_fidelity_dataset_percentage = 0.8
        
        epsilon=0.005
        all_meet_condition = False
        
        request = controller.get_request()  
        dataset_id = request.dataset_id
        training_id= controller.get_training_id()
        
        user_id= request.user_id
        model_list = controller.get_data_storage().get_models(user_id, training_id, dataset_id)
        models_accuracy = {entry['auto_ml_solution']: entry['test_score'].get(':accuracy', 0) for entry in model_list}
        data_store = controller.get_data_storage().get_training(user_id,training_id)
        try:
            parent = data_store[1]['parent_training_id']
        except KeyError:
            parent = "none"
            
        if parent != "none":
                parent_training_id = parent
                parent_model_list = controller.get_data_storage().get_models(user_id, parent_training_id, dataset_id)
                models_accuracy_parent = {entry['auto_ml_solution']: entry['test_score'].get(':accuracy', 0) for entry in parent_model_list}
                print(f"Parent Model List: {parent_model_list}")
                if models_accuracy.keys() != models_accuracy_parent.keys():
                    print("Dictionaries do not have the same keys.")
                else:
                    all_meet_condition = True  # Flag to check if all keys meet the condition
                    # Iterate through each key-value pair in acc_1
                    for key in models_accuracy:
                    # Compare the accuracy of each Model(key) in both the current and parent model list
                        if  ((models_accuracy_parent[key]!=0) & (models_accuracy[key]!=0) & (models_accuracy_parent[key] + epsilon < models_accuracy[key])):
                             all_meet_condition = False
                    if all_meet_condition:
                        controller.disable_strategy('evaluation.optimum_strategy')
                        
        # start a new a training run with 80% of the data and double the runtime limit if the condition is not met             
        if not all_meet_condition:               
            request = controller.get_request()  
            request_copy = copy.deepcopy(request)
            request_copy.configuration.runtime_limit = initial_runtime_limit*1.5

            # start a new training run 
            strategy_controller = StrategyController(
                    controller.get_data_storage(), request_copy, controller.get_explainable_lock(),
                    multi_fidelity_callback=self.do_optimum_strategy_callback,
                    multi_fidelity_level=multi_fidelity_dataset_percentage
            )
            data_storage = controller.get_data_storage()
            
            #Create child_training_id and parent_training_id
            data_storage.update_training(user_id, training_id, {"child_training_id": strategy_controller.get_training_id()})
            data_storage.update_training(user_id,  strategy_controller.get_training_id(), {"parent_training_id": training_id})

            strategy_controller.get_adapter_runtime_manager().get_training_request()
            print(f"content of trainingRequest: {strategy_controller.get_adapter_runtime_manager().get_training_request()}\t")
            
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
            self._log.info('Finished evaluation phase')
            controller.set_phase('end')
            controller.disable_strategy('evaluation.finish_training')