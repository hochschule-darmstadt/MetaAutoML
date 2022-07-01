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

        # TODO:
        # train best pipeline?
        # how to export considering alphad3m specialties
        # hot to for the prediction on frontend

        self.__export_pipeline(d3m_obj, os.path.join(get_config_property('output-path'), 'tmp', 'd3m'), pipeline_id)
        d3m_obj.end_session()


    def __export_pipeline(self, automl: d3mi.AutoML, export_dir, pipeline_id):
        """Export alphad3m pipeline"""

        automl.save_pipeline(pipeline_id, export_dir)
        with open(os.path.join(export_dir, pipeline_id, problem_config_filepath), 'w') as writer:
            json.dump(automl.problem_config, writer)
        with open(os.path.join(export_dir, meta_filepath), 'w') as writer:
            json.dump({"id" : pipeline_id}, writer)
        print('INFO: Pipeline exported.')

    def __import_pipeline(self, automl: d3mi.AutoML, export_dir):
        """Import alphad3m pipeline"""
        
        old_pipeline_id = ""
        with open(os.path.join(export_dir, meta_filepath), 'r') as reader:
            old_pipeline_id = json.load(reader)["id"]
        with open(os.path.join(export_dir, old_pipeline_id, problem_config_filepath), 'r') as reader:
            automl.problem_config = json.load(reader)
        automl.load_pipeline(os.path.join(export_dir, old_pipeline_id))
        pipeline_id = automl.get_best_pipeline_id()
        automl.pipelines[pipeline_id]["fitted_id"] = old_pipeline_id
        print("INFO: Pipeline imported.")
        return pipeline_id