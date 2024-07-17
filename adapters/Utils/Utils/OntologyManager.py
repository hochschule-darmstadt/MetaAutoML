from cgitb import reset
import logging
import rdflib
import os
import Queries

from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import SKOS

import json

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
        self.__log = logging.getLogger('OntologyManager')
        #self.__log.setLevel(logging.getLevelName(os.getenv("ONTOLOGY_LOGGING_LEVEL")))
        ontologyPath = os.getenv("ONTOLOGY_PATH")
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

    def get_config_item_by_automl_and_task(self, automl, task) -> tuple:
        """Get dataset types available within the ML Ontology

        Returns:
            GetDatasetTypesResponse: The GRPC response message holding the list of dataset type IRIs
        """
        self.__log.debug("get_dataset_types: get all dataset types")
        result = []
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_CONFIGURATION_ITEMS_BY_AUTOML_AND_TASK,
                        initNs={"skos": SKOS})
        automl = self.__iri_to_uri_ref(automl)
        task = self.__iri_to_uri_ref(task)
        queryResult = self.__execute_query(q, {"automl": automl, "task": task})
        for row in queryResult:
            result.append(row.para.replace(ML_ONTOLOGY_NAMESPACE, ":"))
        return result

    def get_broader_type_and_datatype_for_config_item(self, config_item_id) -> tuple:
        """Get dataset types available within the ML Ontology

        Returns:
            GetDatasetTypesResponse: The GRPC response message holding the list of dataset type IRIs
        """
        self.__log.debug("get_dataset_types: get all dataset types")
        result = ()
        q = prepareQuery(Queries.ONTOLOGY_QUERY_GET_BROADER_AND_DATATYPE_FOR_CONFIG_PARA_BY_IRI,
                        initNs={"skos": SKOS})
        config_item = self.__iri_to_uri_ref(config_item_id)
        queryResult = self.__execute_query(q, {"iri": config_item})
        for row in queryResult:
            result = (row.broader.replace(ML_ONTOLOGY_NAMESPACE, ":"), row.type.replace(ML_ONTOLOGY_NAMESPACE, ":"))
        return result

    def __normalize_iri_to_colon(self, iri: str) -> str:
        if iri is not None:
            return iri.replace(ML_ONTOLOGY_NAMESPACE, ":")
        return None

    def __iri_to_uri_ref(self, iri: str) -> str:
        return rdflib.URIRef(ML_ONTOLOGY_NAMESPACE + iri.replace(":", ""))
