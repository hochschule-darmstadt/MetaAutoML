import json, time
from rule_engine import Rule, Context, DataType, type_resolver_from_dict
from Controller_bgrpc import DataType as GrpcDataType
from .AbstractStrategy import IAbstractStrategy
from ..Controller import StrategyController
from ..Blackboard import Blackboard

class DataPreparationStrategyController(IAbstractStrategy):
    def RegisterRules(self):
        data_preparation_context = Context(
            type_resolver=type_resolver_from_dict({
                'phase': DataType.STRING,
                'dataset_analysis': DataType.MAPPING(
                    key_type=DataType.STRING,
                    value_type=DataType.UNDEFINED
                )
            })
        )

        self.RegisterRule(
            'data_preparation.ignore_redundant_features',
            Rule("phase == 'preprocessing' and not dataset_analysis['duplicate_columns'].is_empty", context=data_preparation_context),
            self.DoIgnoreRedundantFeatures
        )

        self.RegisterRule(
            'data_preparation.ignore_redundant_samples',
            Rule("phase == 'preprocessing' and not dataset_analysis['duplicate_rows'].is_empty", context=data_preparation_context),
            self.DoIgnoreRedundantSamples
        )

        self.RegisterRule(
            'data_preparation.split_large_datasets',
            Rule("phase == 'preprocessing' and dataset_analysis['number_of_rows'] > 10000", context=data_preparation_context),
            self.DoSplitLargeDatasets
        )

        self.RegisterRule(
            'data_preparation.finish_preprocessing',
            Rule("""
                phase == 'preprocessing' and
                dataset_analysis != null and
                not dataset_analysis.is_empty and
                dataset_analysis['duplicate_columns'].is_empty and
                dataset_analysis['duplicate_rows'].is_empty and
                dataset_analysis['number_of_rows'] <= 10000
            """, context=data_preparation_context),
            self.DoFinishPreprocessing
        )

    def DoIgnoreRedundantFeatures(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        duplicate_columns = state.get("dataset_analysis", {}).get("duplicate_columns", [])
        ignored_columns = []

        agent = controller.blackboard.GetAgent('automl-session')
        if not agent or not agent.session:
            raise RuntimeError('Could not access AutoML session agent!')
        dataset_configuration = json.loads(agent.session.configuration.dataset_configuration)

        time.sleep(20) # FIXME: Remo

        for column_a, column_b in duplicate_columns:
            self._log.info(f'Encountered redundant feature "{column_b}" (same as "{column_a}"), ingoring the column.')
            dataset_configuration['features'][column_b] = GrpcDataType.DATATYPE_IGNORE
            ignored_columns.append(column_b)

        agent.session.configuration.dataset_configuration = json.dumps(dataset_configuration) 

        # IDEA: Update dataset analysis accordingly (may not be neccessary)
        blackboard.UpdateState('dataset_analysis', { 'duplicate_columns': [] }, True)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.DisableStrategy('data_preparation.ignore_redundant_features')

        return { 'ignored_columns': ignored_columns }

    def DoIgnoreRedundantSamples(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        duplicate_rows = state.get("dataset_analysis", {}).get("duplicate_rows")
        self._log.info(f'Encountered redundant samples ({duplicate_rows}), omitting these rows..')

        # TODO: Re-implement the row omitting logic
        # Preparation (maybe reusable utility function):
        #   - Copy dataset from dataset folder to training folder
        #   - Change adapter/session config dataset path
        # Load dataset from (new) dataset path
        # Remove rows that should be omitted
        
        # IDEA: Update dataset analysis accordingly (may not be neccessary)
        blackboard.UpdateState('dataset_analysis', { 'duplicate_rows': [] }, True)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.DisableStrategy('data_preparation.ignore_redundant_samples')

    def DoSplitLargeDatasets(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        number_of_rows = state.get("dataset_analysis", {}).get("number_of_rows")
        self._log.info(f'Encountered large input dataset ({number_of_rows} rows), splitting..')

        # TODO: Re-implement the data splitting (check new structure!)

        # IDEA: Update dataset analysis accordingly (may not be neccessary)
        blackboard.UpdateState('dataset_analysis', { 'number_of_rows': 10000 }, True)

        # Finished action (should only run once, therefore disable the strategy rule)
        controller.DisableStrategy('data_preparation.split_large_datasets')

    def DoFinishPreprocessing(self, state: dict, blackboard: Blackboard, controller: StrategyController):
        self._log.info(f'Finished data preparation, advancing to phase "running"..')
        controller.SetPhase('running')
        controller.DisableStrategy('data_preparation.finish_preprocessing')