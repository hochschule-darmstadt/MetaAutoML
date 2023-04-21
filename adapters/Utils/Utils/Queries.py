"""
SPARQL query to get the broader config item and the datatype
"""
ONTOLOGY_QUERY_GET_BROADER_AND_DATATYPE_FOR_CONFIG_PARA_BY_IRI = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?broader ?type
            WHERE {
            ?iri a :Configuration_item ;
                        skos:broader ?broader ;
                        :has_datatype ?type .
            }
            """

"""
SPARQL query to get all configuration items by automl and ml taks
"""
ONTOLOGY_QUERY_GET_CONFIGURATION_ITEMS_BY_AUTOML_AND_TASK = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?para
            WHERE {
            ?col a :Configuration_item ;
                 :automl_solution ?automl ;
                 :ml_task ?task ;
                 :parameter_value ?para .
            }
            """
