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
    Ontology Manager provides functionality to interact with the ML Ontology
    """

    def __init__(self):        
        """Initiate a new OntologyManager instance
        """
        with MeasureDuration() as m:
            self.__log = logging.getLogger('OntologyManager')
            self.__log.setLevel(logging.getLevelName(os.getenv("ONTOLOGY_LOGGING_LEVEL")))
            ontologyPath = os.path.join(os.path.dirname(__file__), 'ML_Ontology.ttl')
            self.__ontologyGraph = rdflib.Graph()
            self.__ontologyGraph.parse(ontologyPath, format='turtle')
            self.__log.info("__init__: new Ontology Manager created...")

    def __execute_query(self, query: str, binding: dict=None) -> list:
        """Execute the SPARQL query on the ML Ontology

        Args:
            query (str): SPARQL query string
            binding (dict, optional): Query parameter dictonary used within the SPARQL query. Defaults to None.

        Returns:
            list: Item rows returned by the ontology as a result of the executed SPARQL query
        """
        resultList = []
        self.__log.debug(f"__execute_query: Executing SPARQL query: {query}")
        queryResult = self.__ontologyGraph.query(query, initBindings=binding)
        self.__log.debug(f"__execute_query: Received {len(queryResult)} results")
        return queryResult

    def get_auto_ml_solutions_for_configuration(self, request: GetAutoMlSolutionsForConfigurationRequest) -> GetAutoMlSolutionsForConfigurationResponse:
        """Get AutoML solutions matching the provided configuration

        Args:
            request (GetAutoMlSolutionsForConfigurationRequest): The GRPC request message holding the configuration dictonary

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if the configuration does not hold a Task key or has an empty value for the Task key

        Returns:
            GetAutoMlSolutionsForConfigurationResponse: The GRPC response message holding the list of AutoML solution IRIs
        """
        result = GetAutoMlSolutionsForConfigurationResponse()
        if "task" not in request.configuration or (len(request.configuration["task"]) == 0):  # Check if task parameter is contained, we require it for a successful query
            self.__log.error("get_auto_ml_solutions_for_configuration: Task parameter not set or is empty")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, "Task parameter not set or is empty")
        
        
        task = rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + request.configuration["task"].replace(":", ""))
        #task = rdflib.Literal(request.configuration["task"])
        if "library" not in request.configuration or (len(request.configuration["library"]) == 0): # if libraries list is empty we do not query for library filter
            self.__log.debug(f'get_auto_ml_solutions_for_configuration: querying for task only {request.configuration["task"]}')
            q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_COMPATIBLE_AUTO_ML_SOLUTIONS_FOR_TASK,
                        initNs={"skos": SKOS})
            queryResult = self.__execute_query(q, {"task": task})
            for row in queryResult:
                result.auto_ml_solutions.append(row.automl.replace(ML_ONTOLOGY_NAMESPACE, ":"))
            return result
        else:
            self.__log.debug(f'get_auto_ml_solutions_for_configuration: querying for task {request.configuration["task"]} and libraries {request.configuration["library"]}')
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
        """Get dataset types available within the ML Ontology

        Returns:
            GetDatasetTypesResponse: The GRPC response message holding the list of dataset type IRIs
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
        """Get ML libraries for a specific task 

        Args:
            request (GetMlLibrariesForTaskRequest): The GPRC request message holding task IRI

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if the task variable is empty

        Returns:
            GetMlLibrariesForTaskResponse: The GRPC response message holding the list of ML library IRIs
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
        """Get the object information by its IRI

        Args:
            request (GetObjectsInformationRequest): The GRPC request message holding the object IRI

        Returns:
            GetObjectsInformationResponse: The GRPC response message holding the dictonary of object informations
        """
        result = GetObjectsInformationResponse()
        for id in request.ids:
            self.__log.debug(f"get_objects_information: querying for id {id}")
            current_object = ObjectInformation()
            q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_ALL_DETAILS_BY_ID)

            object_id = rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + id.replace(":", ""))
            queryResult = self.__execute_query(q, {"s": object_id})
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

    def get_tasks_for_dataset_type(self, request: GetTasksForDatasetTypeRequest) -> GetTasksForDatasetTypeResponse:
        """Get tasks supported by a dataset type

        Args:
            request (GetTasksForDatasetTypeRequest): The GRPC request message holding the dataset type IRI

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if the dataset type is empty

        Returns:
            GetTasksForDatasetTypeResponse: The GRPC response message holding the list of task IRIs
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
