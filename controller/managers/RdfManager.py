from cgitb import reset
import logging
import rdflib
import os
import Queries
from Controller_bgrpc import *

from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import SKOS

ML_ONTOLOGY_NAMESPACE = "http://h-da.de/ml-ontology/"
RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS_NAMESPACE = "http://www.w3.org/2000/01/rdf-schema#"
XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema#"
SKOS_NAMESPACE = "http://www.w3.org/2004/02/skos/core#"


class RdfManager(object):
    """
    RDF Manager to interact with the remote ML Ontology
    """

    def __init__(self):
        ontologyPath = os.path.join(os.path.dirname(__file__), 'ontology', 'ML_Ontology.ttl')
        self.__ontologyGraph = rdflib.Graph()
        self.__ontologyGraph.parse(ontologyPath, format='turtle')
        self.__log = logging.getLogger()

    def __executeQuery(self, query: str, binding: dict=None) -> list:
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

    def GetCompatibleAutoMlSolutions(self, request: GetCompatibleAutoMlSolutionsRequest) -> GetCompatibleAutoMlSolutionsResponse:
        """
        Retrive all compatible AutoML solutions depending on the configuration
        ---
        Parameter
        1. configuration dictonary
        ---
        Return a list of AutoML names
        """
        result = GetCompatibleAutoMlSolutionsResponse()

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
            result.auto_ml_solutions.append(row.automl.replace(ML_ONTOLOGY_NAMESPACE, ""))
        return result

    def GetDatasetCompatibleTasks(self, request: GetDatasetCompatibleTasksRequest) -> GetDatasetCompatibleTasksResponse:
        """
        Retrive possible AutoML tasks for a given dataset
        ---
        Parameter
        1. dataset name
        ---
        Return a list of compatible AutoML tasks
        """
        result = GetDatasetCompatibleTasksResponse()

        ###TODO change approach, we want to log on upload what a dataset is, now we need to somehow guess it. ATM only tabular data is supported 
        if len(request.dataset_name) == 0:  # Check if dataset name is present, we require it for a successful query
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

    def GetDatasetTypes(self, request: GetDatasetTypesRequest) -> GetDatasetTypesResponse:
        """
        Get all dataset types
        ---
        Return list of all dataset types
        """
        result = GetDatasetTypesResponse()

        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_DATASET_TYPES,
                         initNs={"skos": SKOS})
        
        queryResult = self.__executeQuery(q)
        for row in queryResult:
            result.dataset_types.append(row.type.replace(ML_ONTOLOGY_NAMESPACE, ":"))
        return result

    def GetObjectsInformation(self, request: GetObjectsInformationRequest) -> GetObjectsInformationResponse:
        """
        Get all object information
        ---
        Parameter
        1. object id
        ---
        Return dictonary of object informations
        """
        result = GetObjectsInformationResponse()

        for id in request.ids:
            current_object = ObjectInformation()
            q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_ALL_DETAILS_BY_ID)

            object_id = rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + id.replace(":", ""))
            queryResult = self.__executeQuery(q, {"s": object_id})
            current_object.id = id
            for row in queryResult:
                row.p = row.p.replace(ML_ONTOLOGY_NAMESPACE, ":")
                row.p = row.p.replace(RDF_NAMESPACE, "rdf:")
                row.p = row.p.replace(RDFS_NAMESPACE, "rdfs:")
                row.p = row.p.replace(XSD_NAMESPACE, "xsd:")
                row.p = row.p.replace(SKOS_NAMESPACE, "skos:")
                row.o = row.o.replace(ML_ONTOLOGY_NAMESPACE, ":")
                row.o = row.o.replace(RDF_NAMESPACE, "rdf:")
                row.o = row.o.replace(RDFS_NAMESPACE, "rdfs:")
                row.o = row.o.replace(XSD_NAMESPACE, "xsd:")
                row.o = row.o.replace(SKOS_NAMESPACE, "skos:")
                current_object.informations[row.p] = row.o

            result.object_informations.append(current_object)

        return result


    def GetSupportedMlLibraries(self, request) -> GetSupportedMlLibrariesResponse:
        """
        Retrive all Machine Learn Library for this task by supported AutoMLs
        ---
        Parameter
        1. configuration dictonary
        ---
        Return a list of Machine Learning libraries
        """
        result = GetSupportedMlLibrariesResponse()

        if len(request.task) == 0:  # Check if task parameter has value, we require it for a successful query
            self.__log.exception("task parameter empty")
            result.MlLibraries.append("Task parameter value missing")
            return result

        task = rdflib.Literal(request.task)
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_SUPPORTED_ML_LIBRARIES_FOR_TASK,
                         initNs={"skos": SKOS})

        queryResult = self.__executeQuery(q, {"taskName": task})
        for row in queryResult:
            result.MlLibraries.append(row.library.replace(ML_ONTOLOGY_NAMESPACE, ""))
        return result