import json, time
from rule_engine import Rule, Context, DataType, type_resolver_from_dict
from AdapterRuntimeManagerAgent import AdapterRuntimeManagerAgent
from ControllerBGRPC import DataType as GrpcDataType
from IAbstractStrategy import IAbstractStrategy
from StrategyController import StrategyController
from Blackboard import Blackboard
from CsvManager import CsvManager
import pandas as pd

class PreprocessingStrategyController(IAbstractStrategy):
    global_multi_fidelity_level = 1

    def register_rules(self):
        preprocessing_context = Context(
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
            'preprocessing.ignore_redundant_features',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image') and not dataset_analysis['duplicate_columns'].is_empty", context=preprocessing_context),
            self.do_ignore_redundant_features
        )

        self.register_rule(
            'preprocessing.ignore_redundant_samples',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image') and not dataset_analysis['duplicate_rows'].is_empty", context=preprocessing_context),
            self.do_ignore_redundant_samples
        )

        self.register_rule(
            'preprocessing.split_large_datasets',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image') and dataset_analysis['number_of_rows'] > 10000", context=preprocessing_context),
            self.do_split_large_datasets
        )

        self.register_rule(
            'preprocessing.feature_selection',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image')", context=preprocessing_context),
            self.do_feature_selection
        )

        self.register_rule(
            'preprocessing.pca_feature_extraction',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image')", context=preprocessing_context),
            self.do_pca_feature_extraction
        )
        self.register_rule(
            'preprocessing.do_data_sampling',
            Rule("phase == 'preprocessing' and not (dataset_type == ':image')", context=preprocessing_context),
            self.do_data_sampling
        )


        self.register_rule(
            'preprocessing.finish_preprocessing',
            Rule("""
                phase == 'preprocessing' and
                ((dataset_type == ':image') or (not dataset_analysis.is_empty)) and
                ('preprocessing.ignore_redundant_features' not in enabled_strategies or dataset_analysis['duplicate_columns'].is_empty) and
                ('preprocessing.ignore_redundant_samples' not in enabled_strategies or dataset_analysis['duplicate_rows'].is_empty) and
                ('preprocessing.split_large_datasets' not in enabled_strategies or dataset_analysis['number_of_rows'] <= 10000)
            """, context=preprocessing_context),
            self.do_finish_preprocessing
        )

        # Force enable this strategy to ensure preprocessing always finishes
        self.controller.enable_strategy('preprocessing.finish_preprocessing')

    def do_ignore_redundant_features(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        duplicate_columns = state.get("dataset_analysis", {}).get("duplicate_columns", [])
        ignored_columns = []

        # TODO: Re-implement the row omitting logic
                # Preparation (maybe reusable utility function):
                #   - Copy dataset from dataset folder to training folder
                #   - Change adapter/session config dataset path
                # Load dataset from (new) dataset path
                # Remove rows that should be omitted

        agent: AdapterRuntimeManagerAgent = controller.get_blackboard().get_agent('training-runtime')
        if not agent or not agent.get_adapter_runtime_manager():
            raise RuntimeError('Could not access Adapter Runtime Manager Agent!')
        dataset_configuration = json.loads(agent.get_adapter_runtime_manager().get_training_request().dataset_configuration)

        for column_a, column_b in duplicate_columns:
            self._log.info(f'do_ignore_redundant_features: Encountered redundant feature "{column_b}" (same as "{column_a}"), ingoring the column.')
            dataset_configuration[column_b]['role_selected'] = ":ignore"

        training_request = agent.get_adapter_runtime_manager().get_training_request()
        training_request.dataset_configuration = json.dumps(dataset_configuration)
        agent.get_adapter_runtime_manager().set_training_request(training_request)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('preprocessing.ignore_redundant_features')

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
        controller.disable_strategy('preprocessing.ignore_redundant_samples')

        return { 'ignored_samples': ignored_samples }

    def do_split_large_datasets(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        number_of_rows = state.get("dataset_analysis", {}).get("number_of_rows")
        self._log.info(f'do_split_large_datasets: do_ignore_redundant_samples: Encountered large input dataset ({number_of_rows} rows), splitting..')

        # TODO: Re-implement the data splitting (check new structure!)
        time.sleep(5) # FIXME: Remove this line, only for debugging

        # IDEA: Update dataset analysis accordingly (may not be neccessary)
        blackboard.update_state('dataset_analysis', { 'number_of_rows': 10000 }, True)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('preprocessing.split_large_datasets')

    def do_feature_selection(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        irrelevant_features = state.get("dataset_analysis", {}).get("irrelevant_features", [])

        agent: AdapterRuntimeManagerAgent = controller.get_blackboard().get_agent('training-runtime')
        if not agent or not agent.get_adapter_runtime_manager():
            raise RuntimeError('Could not access Adapter Runtime Manager Agent!')
        dataset_configuration = json.loads(agent.get_adapter_runtime_manager().get_training_request().dataset_configuration)

        for column in irrelevant_features:
            self._log.info(f'do_feature_selection: Encountered irrelevant feature {column}.')
            dataset_configuration[column]['role_selected'] = ":ignore"

        training_request = agent.get_adapter_runtime_manager().get_training_request()
        training_request.dataset_configuration = json.dumps(dataset_configuration)
        agent.get_adapter_runtime_manager().set_training_request(training_request)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('preprocessing.feature_selection')

    def do_pca_feature_extraction(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        agent: AdapterRuntimeManagerAgent = controller.get_blackboard().get_agent('training-runtime')
        if not agent or not agent.get_adapter_runtime_manager():
            raise RuntimeError('Could not access Adapter Runtime Manager Agent!')
        dataset_configuration = json.loads(agent.get_adapter_runtime_manager().get_training_request().dataset_configuration)

        for dcc in dataset_configuration:
            if dataset_configuration[dcc]['role_selected'] != ":ignore":
                if dataset_configuration[dcc]['datatype_selected'] != ":string":
                    if dataset_configuration[dcc]['datatype_selected'] == '' and dataset_configuration[dcc]['datatype_detected'] != ":string":
                        dataset_configuration[dcc]['preprocessing'] = {"pca": True}

        training_request = agent.get_adapter_runtime_manager().get_training_request()
        training_request.dataset_configuration = json.dumps(dataset_configuration)
        agent.get_adapter_runtime_manager().set_training_request(training_request)


        found, dataset = self.__data_storage.get_dataset(training_request.dataset_id)
        self.__dataset_df = CsvManager.read_dataset(self.__dataset["path"], dataset["file_configuration"], dataset["schema"])



        # Finished action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('preprocessing.feature_selection')

    def do_finish_preprocessing(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        if self.global_multi_fidelity_level != 0:
            self._log.info(f'do_finish_preprocessing: Finished data preparation, advancing to phase "running"..')
            controller.set_phase('pre_training')
            controller.disable_strategy('preprocessing.finish_preprocessing')

    def do_data_sampling(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        agent: AdapterRuntimeManagerAgent = controller.get_blackboard().get_agent('training-runtime')
        if not agent or not agent.get_adapter_runtime_manager():
            raise RuntimeError('Could not acess Adapter Runtime Manager Agent!')
        dataset_configuration = json.loads(agent.get_adapter_runtime_manager().get_training_request().dataset_configuration)

        print ("====Here is Data sampling======")
        print(dataset_configuration)
        print("===============================")
        print(state.get("dataset_analysis",{}))

        found, dataset = self.__data_storage.get_dataset(training_request.dataset_id)
        print(found, dataset)
        self.__dataset_df = CsvManager.read_dataset(self.__dataset["path"], dataset["file_configuration"], dataset["schema"])

        training_request = agent.get_adapter_runtime_manager().get_training_request()
        training_request.dataset_configuration = json.dumps(dataset_configuration)
        agent.get_adapter_runtime_manager().set_training_request(training_request)



        #Finishes action (should only run once, therefore disable the strategy rule)
        controller.disable_strategy('preprocessing.data_sampling')

