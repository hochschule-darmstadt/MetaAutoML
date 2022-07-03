import logging
import rdflib
import os
import Controller_pb2
import Controller_pb2_grpc
import Queries

from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import SKOS

ML_ONTOLOGY_NAMESPACE = "http://h-da.de/ml-ontology/"


class RdfManager(object):
    """
    RDF Manager to interact with the remote ML Ontology
    """

    def __init__(self):
        ontologyPath = os.path.join(os.path.dirname(__file__), 'ontology', 'ML_Ontology.ttl')
        self.__ontologyGraph = rdflib.Graph()
        self.__ontologyGraph.parse(ontologyPath, format='turtle')
        self.__log = logging.getLogger()

    def __executeQuery(self, query: str, binding: dict) -> list:
        """
        Execute the SPARQL query on our ML Ontology and convert the result set to usable format
        ---
        Parameter
        1. SPARQL query to execute
        2. Binding dictinary for parameter queries, pass empty dictonary if not required
        ---
        Return a list with string results
        """
        resultList = []
        self.__log.info(f"Executing SPARQL query: {query}")
        queryResult = self.__ontologyGraph.query(query, initBindings=binding)
        self.__log.info(f"Received {len(queryResult)} results")

        # for row in queryResult: #Remove default namespace name from any result
        # resultList.append(row.automl.replace(ML_ONTOLOGY_NAMESPACE, ""))

        return queryResult

    def GetCompatibleAutoMlSolutions(self, request) -> Controller_pb2.GetCompatibleAutoMlSolutionsResponse:
        """
        Retrive all compatible AutoML solutions depending on the configuration
        ---
        Parameter
        1. configuration dictonary
        ---
        Return a list of AutoML names
        """
        result = Controller_pb2.GetCompatibleAutoMlSolutionsResponse()

        if "task" not in request.configuration:  # Check if task parameter is contained, we require it for a successful query
            self.__log.exception("Configuration dictonary does not contain the key task")
            result.AutoMlSolutions.append("Task parameter missing")
            return result

        if len(request.configuration[
                   "task"]) == 0:  # Check if task parameter has value, we require it for a successful query
            self.__log.exception("task key in configuration dictonary has no value")
            result.AutoMlSolutions.append("Task parameter value missing")
            return result

        # TODO add more parameter to query
        # task = rdflib.Literal(u'binary classification')
        task = rdflib.Literal(request.configuration["task"])
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_ACTIVE_AUTOML_FOR_TASK,
                         initNs={"skos": SKOS})

        queryResult = self.__executeQuery(q, {"task": task})
        for row in queryResult:
            result.AutoMlSolutions.append(row.automl.replace(ML_ONTOLOGY_NAMESPACE, ""))
        return result

    def GetDatasetCompatibleTasks(self, request) -> Controller_pb2.GetDatasetCompatibleTasksResponse:
        """
        Retrive possible AutoML tasks for a given dataset
        ---
        Parameter
        1. dataset name
        ---
        Return a list of compatible AutoML tasks
        """
        result = Controller_pb2.GetDatasetCompatibleTasksResponse()

        ###TODO change approach, we want to log on upload what a dataset is, now we need to somehow guess it. ATM only tabular data is supported 
        if len(request.datasetName) == 0:  # Check if dataset name is present, we require it for a successful query
            self.__log.exception("Dataset name is empty")
            result.tasks.append("Dataset name parameter empty")
            return result

        dataset = rdflib.Literal(u"tabular data")
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_TASKS_FOR_DATASET_TYPE,
                         initNs={"skos": SKOS})

        queryResult = self.__executeQuery(q, {"dataset": dataset})
        for row in queryResult:
            result.tasks.append(row.task.replace(ML_ONTOLOGY_NAMESPACE, ""))
        return result

    def GetSupportedMlLibraries(self, request) -> Controller_pb2.GetSupportedMlLibrariesResponse:
        """
        Retrive all Machine Learn Library for this task by supported AutoMLs
        ---
        Parameter
        1. configuration dictonary
        ---
        Return a list of Machine Learning libraries
        """
        result = Controller_pb2.GetSupportedMlLibrariesResponse()

        if len(request.task) == 0:  # Check if task parameter has value, we require it for a successful query
            self.__log.exception("task parameter empty")
            result.MlLibraries.append("Task parameter value missing")
            return result

        task = rdflib.Literal(request.task)
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_SUPPORTED_MACHINE_LEARNING_LIBRARY,
                         initNs={"skos": SKOS})

        queryResult = self.__executeQuery(q, {"taskName": task})
        for row in queryResult:
            result.MlLibraries.append(row.library.replace(ML_ONTOLOGY_NAMESPACE, ""))
        return result

    def GetTasks(self, dataType):
        return