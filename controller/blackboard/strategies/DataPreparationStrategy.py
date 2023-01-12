import json, time
from rule_engine import Rule, Context, DataType, type_resolver_from_dict
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from ControllerBGRPC import DataType as GrpcDataType
from IAbstractStrategy import IAbstractStrategy
from StrategyController import StrategyController
from Blackboard import Blackboard

class DataPreparationStrategyController(IAbstractStrategy):
    def register_rules(self):
        data_preparation_context = Context(
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
            'data_preparation.ignore_redundant_features',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image') and not dataset_analysis['duplicate_columns'].is_empty", context=data_preparation_context),
            self.do_ignore_redundant_features
        )

        self.register_rule(
            'data_preparation.ignore_redundant_samples',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image') and not dataset_analysis['duplicate_rows'].is_empty", context=data_preparation_context),
            self.do_ignore_redundant_samples
        )
        
        self.register_rule(
            'data_preparation.multi_fidelity_optimization',
            Rule("phase == 'preprocessing'", context=data_preparation_context),
            self.multi_fidelity_optimization
        )

        self.register_rule(
            'data_preparation.split_large_datasets',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image') and dataset_analysis['number_of_rows'] > 10000", context=data_preparation_context),
            self.do_split_large_datasets
        )

        self.register_rule(
            'data_preparation.data_encoding_for_categories',
            Rule("phase == 'preprocessing' and ('\"DatatypeSelected\": \":categorical\"' in training_runtime['configuration']['datasetConfiguration'])", context=data_preparation_context),
            self.do_data_encoding_for_categories
        )

        self.register_rule(
            'data_preparation.finish_preprocessing',
            Rule("""
                phase == 'preprocessing' and
                ((dataset_type == ':image') or (not dataset_analysis.is_empty)) and
                ('data_preparation.ignore_redundant_features' not in enabled_strategies or dataset_analysis['duplicate_columns'].is_empty) and
                ('data_preparation.ignore_redundant_samples' not in enabled_strategies or dataset_analysis['duplicate_rows'].is_empty) and
                ('data_preparation.split_large_datasets' not in enabled_strategies or dataset_analysis['number_of_rows'] <= 10000)
            """, context=data_preparation_context),
            self.do_finish_preprocessing
        )

        # Force enable this strategy to ensure preprocessing always finishes
        self.controller.enable_strategy('data_preparation.finish_preprocessing')

    def multi_fidelity_optimization(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        # disable Strategy 
        controller.disable_strategy('data_preparation.multi_fidelity_optimization')
        ##TODO

        

        #return { 'ignored_columns': ignored_columns }
    
    def do_ignore_redundant_features(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        duplicate_columns = state.get("dataset_analysis", {}).get("duplicate_columns", [])
        ignored_columns = []

        agent: AdapterRuntimeManagerAgent = controller.blackboard.get_agent('training-runtime')
        if not agent or not agent.get_adapter_runtime_manager():
            raise RuntimeError('Could not access Adapter Runtime Manager Agent!')
        dataset_configuration = json.loads(agent.get_adapter_runtime_manager().get_training_request().dataset_configuration)

        dataset_configuration['features'] = {}
        for column_a, column_b in duplicate_columns:
            self._log.info(f'do_ignore_redundant_features: Encountered redundant feature "{column_b}" (same as "{column_a}"), ingoring the column.')
            dataset_configuration['features'][column_b] = GrpcDataType.DATATYPE_IGNORE
            ignored_columns.append(column_b)

        training_request = agent.get_adapter_runtime_manager().get_training_request()
        training_request.dataset_configuration = json.dumps(dataset_configuration)
        agent.get_adapter_runtime_manager().set_training_request(training_request)
        
        # IDEA: Update dataset analysis accordingly (may not be neccessary)
        blackboard.update_state('dataset_analysis', { 'duplicate_columns': [] }, True)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('data_preparation.ignore_redundant_features')

        return { 'ignored_columns': ignored_columns }

    def do_ignore_redundant_samples(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        duplicate_rows = state.get("dataset_analysis", {}).get("duplicate_rows")

        ignored_samples = []

        agent: AdapterRuntimeManagerAgent = controller.get_blackboard().get_agent('training-runtime')
        if not agent or not agent.get_adapter_runtime_manager():
            raise RuntimeError('Could not access Adapter Runtime Manager Agent!')
        dataset_configuration = json.loads(agent.get_adapter_runtime_manager().get_training_request().dataset_configuration)

        dataset_configuration['ignored_samples'] = {}
        for row_a, row_b in duplicate_rows:
            self._log.info(f'do_ignore_redundant_samples: Encountered redundant sample "{row_a}" (same as "{row_b}"), ingoring the sample.')
            ignored_samples.append(row_b)
        
        dataset_configuration['ignored_samples'] = ignored_samples

        training_request = agent.get_adapter_runtime_manager().get_training_request()
        training_request.dataset_configuration = json.dumps(dataset_configuration)
        agent.get_adapter_runtime_manager().set_training_request(training_request)

        # IDEA: Update dataset analysis accordingly (may not be neccessary)
        blackboard.update_state('dataset_analysis', { 'duplicate_rows': [] }, True)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('data_preparation.ignore_redundant_samples')

        return { 'ignored_samples': ignored_samples }

    def do_split_large_datasets(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        number_of_rows = state.get("dataset_analysis", {}).get("number_of_rows")
        self._log.info(f'do_split_large_datasets: do_ignore_redundant_samples: Encountered large input dataset ({number_of_rows} rows), splitting..')

        # TODO: Re-implement the data splitting (check new structure!)
        time.sleep(5) # FIXME: Remove this line, only for debugging

        # IDEA: Update dataset analysis accordingly (may not be neccessary)
        blackboard.update_state('dataset_analysis', { 'number_of_rows': 10000 }, True)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('data_preparation.split_large_datasets')

    def do_data_encoding_for_categories(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        column_datatypes = json.loads(state.get("training_runtime", {}).get("configuration", {}).get("datasetConfiguration", str))["column_datatypes"]
        encoded_columns = {}

        agent: AdapterRuntimeManagerAgent = controller.get_blackboard().get_agent('training-runtime')
        if not agent or not agent.get_adapter_runtime_manager():
            raise RuntimeError('Could not access Adapter Runtime Manager Agent!')
        dataset_configuration = json.loads(agent.get_adapter_runtime_manager().get_training_request().dataset_configuration)

        dataset_configuration['encoded_columns'] = {}
        for key, column_datatype in column_datatypes.items():
            if column_datatype == 4:
                self._log.info(f'do_data_encoding_for_categories: Add "{key}" to encoded_columns.')
                encoded_columns[key] = []

            dataset_configuration['encoded_columns'] = encoded_columns

        training_request = agent.get_adapter_runtime_manager().get_training_request()
        training_request.dataset_configuration = json.dumps(dataset_configuration)
        agent.get_adapter_runtime_manager().set_training_request(training_request)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('data_preparation.data_encoding_for_categories')

        return { 'encoded_columns': encoded_columns }

    def do_finish_preprocessing(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        self._log.info(f'do_finish_preprocessing: Finished data preparation, advancing to phase "running"..')
        controller.set_phase('running')
        controller.disable_strategy('data_preparation.finish_preprocessing')