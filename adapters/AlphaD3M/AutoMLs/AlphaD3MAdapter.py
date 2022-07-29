import d3m_interface as d3mi
import json
import os, sys

from AbstractAdapter import AbstractAdapter
from AdapterUtils import read_tabular_dataset_training_data, prepare_tabular_dataset, export_model
from JsonUtil import get_config_property
from AdapterUtils import export_model, prepare_tabular_dataset, data_loader


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
        """
        Execute the ML task
        """
        if self._configuration["task"] == ":tabular_classification":
            self.__tabular_classification()

    def __export_model(self, model: d3mi.AutoML):
        path_to_training = os.path.join(get_config_property('output-path'),
            self._configuration["training_id"])
        model.save_pipeline(model.get_best_pipeline_id(), path_to_training)

        with open(path_to_training + "/problem_config.json", "w") as file:
            json.dump(model.problem_config, file)
        
        file_path = os.path.join(get_config_property("job-file-path"),
                             get_config_property("job-file-name"))
        with open(file_path, 'r') as file:
            process_json = json.load(file)
            process_json["pipeline_id"] = model.get_best_pipeline_id()
        with open(file_path, "w") as file:
            json.dump(process_json, file)

    def __tabular_classification(self):
        """Execute the classification task"""
        self.df, test = data_loader(self._configuration)
        X, y = prepare_tabular_dataset(self.df, self._configuration)

        d3m_obj = d3mi.AutoML(os.path.join(get_config_property(
            'output-path'), self._configuration["training_id"], "d3mTmp"), "AlphaD3M", "pypi")
        d3m_obj.search_pipelines(self._configuration["file_location"]+"/"+self._configuration["file_name"],
                                time_bound=int(self._configuration["runtime_constraints"]["runtime_limit"]),
                                time_bound_run=int(self._configuration["runtime_constraints"]["runtime_limit"]),
                                target=self._configuration["configuration"]["target"]["target"],
                                task_keywords=["classification", "multiClass", "tabular"],
                                metric="accuracy")

        pipeline_id = d3m_obj.get_best_pipeline_id()
        d3m_obj.train(pipeline_id)

        self.__export_model(d3m_obj)

        d3m_obj.end_session()