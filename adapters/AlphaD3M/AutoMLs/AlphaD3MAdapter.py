import d3m_interface as d3mi
import pandas
import os, sys

from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data, prepare_tabular_dataset


class AlphaD3MAdapter(AbstractAdapter):
    """
    Implementation of the AutoML functionality for AlphaD3MAdapter
    """

    def __init__(self, configuration: dict):
        """
        Init a new instance of AlphaD3MAdapter
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        super(AlphaD3MAdapter, self).__init__(configuration)

    def start(self):
        """Execute the ML task"""
        if True:
            if self._configuration["task"] == 1:
                self.__tabular_classification()

    def __tabular_classification(self):
        """Execute the classification task"""
        self.df = read_tabular_dataset_training_data(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        # TODO: Implementation of classification by alphad3m here
        d3m_obj = d3mi.AutoML(os.path.join(sys.path[0], "d3mTmp"),
                                "AlphaD3M", "pypi")
        d3m_obj.search_pipelines(self._configuration["file_location"]+"/"+self._configuration["file_name"],
                                time_bound=int(self._configuration["runtime_constraints"]["runtime_limit"]/60),
                                time_bound_run=int(self._configuration["runtime_constraints"]["runtime_limit"]/60),
                                target=self._configuration["tabular_configuration"]["target"]["target"],
                                task_keywords=["classification", "multiClass", "tabular"],
                                metric="accuracy")
        d3m_obj.plot_leaderboard()

        print("----------\n"*10)
