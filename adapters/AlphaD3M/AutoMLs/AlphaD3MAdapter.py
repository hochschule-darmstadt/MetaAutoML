import d3m_interface as d3mi
import json
import os, sys

from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data, prepare_tabular_dataset, export_model
from JsonUtil import get_config_property


meta_filepath = 'model.meta.json'
problem_config_filepath = "problem_config.json"

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

        d3m_obj = d3mi.AutoML(os.path.join(sys.path[0], "d3mTmp"),
                                "AlphaD3M", "pypi")
        d3m_obj.search_pipelines(self._configuration["file_location"]+"/"+self._configuration["file_name"],
                                time_bound=int(self._configuration["runtime_constraints"]["runtime_limit"]/60),
                                time_bound_run=int(self._configuration["runtime_constraints"]["runtime_limit"]/60),
                                target=self._configuration["tabular_configuration"]["target"]["target"],
                                task_keywords=["classification", "multiClass", "tabular"],
                                metric="accuracy")

        pipeline_id = d3m_obj.get_best_pipeline_id()
        d3m_obj.train(pipeline_id)

        export_model(d3m_obj, "model_alphad3m.p")

        d3m_obj.end_session()