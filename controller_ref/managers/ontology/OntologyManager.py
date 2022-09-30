from cgitb import reset
import logging
import rdflib
import os
import Queries
from ControllerBGRPC import *

from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import SKOS

import json
from MeasureDuration import MeasureDuration

ML_ONTOLOGY_NAMESPACE = "http://h-da.de/ml-ontology/"
RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS_NAMESPACE = "http://www.w3.org/2000/01/rdf-schema#"
XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema#"
SKOS_NAMESPACE = "http://www.w3.org/2004/02/skos/core#"

#ontologyPath = os.path.join(os.path.dirname(__file__), 'ML_Ontology.ttl')
#ontologyGraph = rdflib.Graph()
#ontologyGraph.parse(ontologyPath, format='turtle')

class OntologyManager(object):
    """
    RDF Manager to interact with the remote ML Ontology
    """

    def __init__(self):        
        with MeasureDuration() as m:
            self.__log = logging.getLogger('OntologyManager')
            self.__log.setLevel(logging.getLevelName(os.getenv("ONTOLOGY_LOGGING_LEVEL")))
            ontologyPath = os.path.join(os.path.dirname(__file__), 'ML_Ontology.ttl')
            self.__ontologyGraph = rdflib.Graph()
            self.__ontologyGraph.parse(ontologyPath, format='turtle')
            self.__log.info("__init__: new Ontology Manager created...")

    def __execute_query(self, query: str, binding: dict=None) -> list:
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
        self.__log.debug(f"__execute_query: Executing SPARQL query: {query}")
        queryResult = self.__ontologyGraph.query(query, initBindings=binding)
        self.__log.debug(f"__execute_query: Received {len(queryResult)} results")

        # for row in queryResult: #Remove default namespace name from any result
        # resultList.append(row.automl.replace(ML_ONTOLOGY_NAMESPACE, ""))

        return queryResult

    def get_auto_ml_solutions_for_configuration(self, request: GetAutoMlSolutionsForConfigurationRequest) -> GetAutoMlSolutionsForConfigurationResponse:
        """
        Retrive all compatible AutoML solutions depending on the configuration
        ---
        Parameter
        1. configuration dictonary
        ---
        Return a list of AutoML names
        """
        result = GetAutoMlSolutionsForConfigurationResponse()
        if (len(request.task) == 0):  # Check if task parameter is contained, we require it for a successful query
            self.__log.error("get_auto_ml_solutions_for_configuration: Task parameter is empty")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, "Task parameter is empty")
        
        
        task = rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + request.configuration["task"].replace(":", ""))
        #task = rdflib.Literal(request.configuration["task"])
        if request.libraries.count == 0:  # if libraries list is empty we do not query for library filter
            self.__log.debug(f"get_auto_ml_solutions_for_configuration: querying for task only {request.task}")
            q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_COMPATIBLE_AUTO_ML_SOLUTIONS_FOR_TASK,
                        initNs={"skos": SKOS})
            queryResult = self.__execute_query(q, {"task": task})
            for row in queryResult:
                result.auto_ml_solutions.append(row.automl.replace(ML_ONTOLOGY_NAMESPACE, ":"))
            return result
        else:
            self.__log.debug(f"get_auto_ml_solutions_for_configuration: querying for task {request.task} and libraries {request.libraries}")
            for lib in json.loads(request.configuration["library"]):
                library = rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + lib.replace(":", ""))
                #library = rdflib.Literal(request.configuration["library"])
                q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_COMPATIBLE_AUTO_ML_SOLUTIONS_FOR_TASK_AND_LIBRARIES,
                            initNs={"skos": SKOS})
                queryResult = self.__execute_query(q, {"task": task, "lib": library})
                
                for row in queryResult:
                    solution = row.automl.replace(ML_ONTOLOGY_NAMESPACE, ":")
                    if solution not in result.auto_ml_solutions:
                        result.auto_ml_solutions.append(solution)
            return result
        

        # TODO add more parameter to query
        # task = rdflib.Literal(u'binary classification')

    def get_dataset_types(self) -> GetDatasetTypesResponse:
        """
        Get all dataset types
        ---
        Return list of all dataset types
        """
        result = GetDatasetTypesResponse()
        self.__log.debug("get_dataset_types: get all dataset types")
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_DATASET_TYPES,
                        initNs={"skos": SKOS})
        
        queryResult = self.__execute_query(q)
        for row in queryResult:
            result.dataset_types.append(row.type.replace(ML_ONTOLOGY_NAMESPACE, ":"))
        return result


    def get_ml_libraries_for_task(self, request: GetMlLibrariesForTaskRequest) -> GetMlLibrariesForTaskResponse:
        """
        Retrive all Machine Learn Library for this task by supported AutoMLs
        ---
        Parameter
        1. configuration dictonary
        ---
        Return a list of Machine Learning libraries
        """
        result = GetMlLibrariesForTaskResponse()
        if len(request.task) == 0:  # Check if task parameter has value, we require it for a successful query
            self.__log.error("get_ml_libraries_for_task: Task parameter is empty")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, "Task parameter is empty")

        self.__log.debug(f"get_ml_libraries_for_task: querying for task {request.task}")
        task = rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + request.task.replace(":", ""))
        #task = rdflib.Literal(request.task)
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_SUPPORTED_ML_LIBRARIES_FOR_TASK,
                        initNs={"skos": SKOS})

        queryResult = self.__execute_query(q, {"task": task})
        for row in queryResult:
            result.ml_libraries.append(row.lib.replace(ML_ONTOLOGY_NAMESPACE, ":"))
        return result

    def get_objects_information(self, request: GetObjectsInformationRequest) -> GetObjectsInformationResponse:
        """
        SEE PROTO #TODO
        ---
        Parameter
        1. SEE PROTO #TODO
        ---
        Return SEE PROTO #TODO
        """
        result = GetObjectsInformationResponse()
        for id in request.identifiers:
            self.__log.debug(f"get_objects_information: querying for identifier {id}")
            current_object = ObjectInformation()
            q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_ALL_DETAILS_BY_ID)

            object_id = rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + id.replace(":", ""))
            queryResult = self.__execute_query(q, {"s": object_id})
            current_object.identifier = id
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

    def get_tasks_for_dataset_type(self, request: GetTasksForDatasetTypeRequest) -> GetTasksForDatasetTypeResponse:
        """
        Retrive possible AutoML tasks for a given dataset
        ---
        Parameter
        1. dataset name
        2. dataset type
        ---
        Return a list of compatible AutoML tasks
        """
        result = GetTasksForDatasetTypeResponse()
        if len(request.dataset_type) == 0:  # check if dataset type is present, we require it for a successful query
            self.__log.error("get_tasks_for_dataset_type: Dataset type is empty")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, "Dataset type is empty")

        self.__log.debug(f"get_tasks_for_dataset_type: querying for dataset type {request.dataset_type}")
        # dataset = rdflib.Literal(u"tabular data")
        dataset_type = rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + request.dataset_type.replace(":", ""))
        #dataset_type = rdflib.Literal(datasetType)
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_TASKS_FOR_DATASET_TYPE,
                        initNs={"skos": SKOS})

        queryResult = self.__execute_query(q, {"dataset_type": dataset_type})
        for row in queryResult:
            result.tasks.append(row.task.replace(ML_ONTOLOGY_NAMESPACE, ":"))
        return result
