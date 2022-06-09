import logging
from durable.lang import ruleset, when_all, m, item

class DataPreparationStrategyController(object):
    def __init__(self) -> None:
        self.__log = logging.getLogger()
        self.__log.debug(f'Registered data preparation strategy controller.')
        self.RegisterRules()

    def RegisterRules(self):
        with ruleset('state_update'): # FIXME: or dataset_analysis
            @when_all((m.phase == 'data_preparation') & (m.dataset_metrics.number_of_rows > 100000))
            def split_large_datasets(c):
                self.__log.info(f'Encountered large input dataset ({c.m.dataset_metrics.number_of_rows} rows), splitting..')
                # TODO: Split input dataset into smaller subsets?
                c.m.dataset_metrics.number_of_rows = 1000

            @when_all((m.phase == 'data_preparation') & (m.dataset_metrics.na_columns.anyItem(item > 0)))
            def omit_empty_columns(c):
                self.__log.info(f'Found empty columns in the input dataset ({c.m.dataset_metrics.na_columns})!')
                # TODO: Omit the empty columns from the input datset