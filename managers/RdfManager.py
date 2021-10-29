import logging

from SPARQLWrapper import SPARQLWrapper, JSON

ONTOLOGY_ENDPOINT = ""

class RdfManager(object):
    """
    RDF Manager to interact with the remote ML Ontology
    """
    def __init__(self):
        self.__log = logging.getLogger()

    def __executeSelectQuery(self, query: str):
        """
        Execute a given SPARQL query on the remote ML Ontology
        ---
        Parameter
        1. Query string to be executed
        ---
        Return a result dictionary, if the dictonary is empty there is no result or an exception occured
        """
        sparql = SPARQLWrapper(ONTOLOGY_ENDPOINT)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = {}
        try:
            results = sparql.query().conver()
            if not results:     #Check for any result
                self.__log.exception("Query return no result: query %s, message: %s" % (query, ex.msg))
            
        except SPARQLWrapperException as ex:
            self.__log.exception("Error while executing query: query %s, message: %s" % (query, ex.msg))
            results = {}

        return results      #No matter the outcome, we return results. The caller function must decide what to do


    def GetAutoMls(self):
        return {}

    def GetTasks(self, dataType):
        query = """"
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        """"